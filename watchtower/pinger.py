import irc.client
import irc.connection
import sqlalchemy
import ssl
import threading
import yaml

from datetime import datetime, timedelta

from . import db
from .notification_constants import notif_messages, notif_name
from .sde import MapDenormalize
from .util.date import utc


log = __import__('logging').getLogger(__name__)


DT_FORMAT = "%Y-%m-%d %H:%M"


class Pinger(threading.Thread):
    """Pulls notifications from the queue, formats them, and passes them off to
    IrcSender"""

    def __init__(self, config, api, input_queue):
        super(Pinger, self).__init__()

        self.irc_sender = IrcSender(config)
        self.irc_sender.daemon = True

        self.api = api

        sde_engine = sqlalchemy.create_engine(config.get('sde', 'sqlalchemy.uri'))
        SdeSession = db.sessionmaker(bind=sde_engine)
        self.sde_session = SdeSession()

        self.input_queue = input_queue

    def run(self):
        self.irc_sender.start()
        while True:
            try:
                notif = self.input_queue.get()
                formatted_notif = self.format(notif)
                log.info("New notification: %s", formatted_notif)
                self.irc_sender.send(formatted_notif)
                self.input_queue.task_done()
            except:
                log.exception("problem sending notification")

    def format(self, notif):
        return "[{}] ({} ago) {}".format(
            notif.sent_date.strftime(DT_FORMAT),
            self.format_ago(notif.sent_date),
            self.format_message(notif)
        )

    def format_ago(self, dt):
        # TODO: rounding? e.g 1d1h59m will show as "1d1h", but maybe we'd rather "1d2h".
        if dt.tzinfo:
            log.info("aware")
            ago = datetime.now(utc) - dt
        else:
            log.info("unaware")
            ago = datetime.utcnow() - dt
        days_ago = ago.days
        hours_ago = ago.seconds / 60 / 60
        minutes_ago = (ago.seconds / 60) % 60
        seconds_ago = ago.seconds % 60
        if days_ago:
            return "{}d{}h".format(days_ago, hours_ago)
        elif hours_ago:
            return "{}h{}m".format(hours_ago, minutes_ago)
        else:
            return "{}m{}s".format(minutes_ago, seconds_ago)

    def format_message(self, notif):
        if notif.type not in notif_messages:
            return notif_name[notif.type]
        try:
            fields = yaml.load(notif.text)
            fields = self.expand_fields(fields)
            return notif_messages[notif.type].format(**fields)
        except Exception:
            log.exception("problem expanding notification %r %r", notif_messages[notif.type], fields)
            return notif_name[notif.type]

    def expand_fields(self, fields):
        # TODO make this more efficient by combining repeated api calls
        return {k: self.expand_field(k, v) for k, v in fields.items()}

    def expand_field(self, k, v):
        try:
            if k.lower().endswith(('allianceid', 'corpid', 'aggressorid')):
                if v == 'null':
                    return 'none'
                else:
                    res = self.api.proxy.eve.CharacterName(ids=str(v))
                    return res.row[0].name
            elif k in ('moonID', 'planetID', 'solarSystemID'):
                with self.sde_session.transaction() as xact:
                    q = xact.query(MapDenormalize).filter_by(itemID=int(v))
                    return q.all()[0].itemName
            elif k in ('shieldLevel', 'shieldValue', 'armorValue', 'hullValue'):
                return int(round(float(v) * 100, 0))
            elif k == 'reinforceExitTime':
                return datetime.fromtimestamp(int(v) / 10000000 - 11644473600, utc).strftime(DT_FORMAT)
            else:
                return v
        except Exception:
            log.exception("problem expanding field %r: %r", k, v)
            return v


class IrcSender(threading.Thread):
    def __init__(self, config):
        super(IrcSender, self).__init__()
        self.irc_server = config.get('irc', 'server')
        self.irc_port = config.getint('irc', 'port')
        self.irc_nick = config.get('irc', 'nick')
        self.irc_username = config.get('irc', 'username')
        self.irc_password = config.get('irc', 'password')
        self.notif_target = config.get('irc', 'notif_target')
        self.reactor = irc.client.Reactor()

        # Lock protects self.conn. Condition signals readiness of self.conn.
        self.conn_lock = threading.Lock()
        self.conn_cond = threading.Condition(self.conn_lock)
        self.conn = None

    def run(self):
        with self.conn_lock:
            self.conn = self.connect()
            self.conn_cond.notify()
        self.reactor.process_forever()

    def connect(self):
        """Returns a ServerConnection"""
        c = self.reactor.server().connect(self.irc_server, self.irc_port, self.irc_nick,
                                          username=self.irc_username,
                                          password=self.irc_password,
                                          connect_factory=irc.connection.Factory(wrapper=ssl.wrap_socket)) 

        # all this does is blocks connect() until connected.
        # wtb py3k nonlocal
        done = [False]
        def on_connect(conn, event):
            done[0] = True
        c.add_global_handler("welcome", on_connect)
        while not done[0]:
            self.reactor.process_once()
        c.remove_global_handler("welcome", on_connect)
        log.info("done connecting")

        return c

    def send(self, formatted_notif):
        with self.conn_lock:
            while self.conn is None:
                self.conn_cond.wait()

        # We can drop the lock now because self.conn is never reset again.
        self.reactor.execute_delayed(0, self.conn.privmsg, (self.notif_target, formatted_notif))

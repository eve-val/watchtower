from __future__ import print_function

import json
import threading

from datetime import datetime

from .model import Notification
from .notification_constants import notif_name, relevant_notif_types
from .util.date import utc


log = __import__('logging').getLogger(__name__)


# TODO: move?
def get_texts(api, token, char_id, notif_ids, retries=2, _retried=0):
    """
    Get notification texts for the given notifications.

    Args:
        [...]
        notif_ids (List[int]): notifications to fetch

    Returns:
        Optional[Dict[int, Optional[str]]]: mapping from notification ID to
            text; text can be None if the server didn't find the notification,
            or the whole dictionary can be None if our request failed.
    """
    log.info("getting texts")
    ids = map(str, notif_ids) * (_retried + 1)
    res = api.proxy.char.NotificationTexts(token=token, characterID=char_id, IDs=','.join(ids))

    if res is None:
        log.info("! core error")
        return None

    if res.success == False:
        if res.reason == 'key.notfound':
            log.info("  key perm not found")
        else:
            log.info("  unknown failure: {} {}".format(res.reason, res.get('detail')))
        return None

    if len(res.row) != len(ids) and retries > 0:
        return get_texts(api, token, char_id, notif_ids, retries-1, _retried+1)

    assert all(len(notif.row) == 1 for notif in res.row)
    return {notif.notificationID: notif.row[0] for notif in res.row}


# TODO: move?
def get_names(api, ids):
    """
    Get names for the given character/corp/alliance IDs.

    Args:
        [...]
        ids (List[int]): entities to fetch

    Returns:
        Optional[Dict[int, Optional[str]]]: mapping from ID to name.
    """
    ids = set(ids)
    log.info("getting names %r", ids)
    res = api.proxy.eve.CharacterName(ids=','.join(map(str, ids)))
    if res is None:
        log.info("! core error")
        return None

    if res.success == False:
        if res.reason == 'key.notfound':
            log.info("  key perm not found")
        else:
            log.info("  unknown failure: {} {}".format(res.reason, res.get('detail')))
        return None

    return {r.characterID: r.name for r in res.row}


class NotificationPoller(threading.Thread):
    def __init__(self, api, token, db_sess, characters, ping_queue=None):
        """
        XXX need spread-out characters
        Args:
            api (bravapi.client.Client)
            token (str)
            db_sess (.db.TransactionOnlySession)
            characters (List[Bunch]): a list of character info, as return from the /core/info api call.
            ping_queue (Queue): An optional queue to post notifications to.
        """
        super(NotificationPoller, self).__init__()
        self.api = api
        self.token = token
        self.db_sess = db_sess
        self.characters = characters
        self.ping_queue = ping_queue

    def run(self):
        while True:
            self.poll_chars()

    def poll_chars(self):
        for c in self.characters:
            self.poll_char(c)

    def poll_char(self, c):
        log.info(c.character.name)
        notifs_res = self.api.proxy.char.Notifications(token=self.token, characterID=c.character.id)

        if notifs_res is None:
            log.info("! core error")
            return

        if notifs_res.success == False:
            if notifs_res.reason == 'key.notfound':
                log.info("  key perm not found")
            else:
                log.info("  unknown failure: {}".format(notifs_res.reason))
            return

        if not notifs_res.row:
            log.info("  no notifications found")
            return

        # filter notif types we don't care about
        relevant_notifs = notifs_res.row
        relevant_notifs = [notif for notif in notifs_res.row if notif.typeID in relevant_notif_types]
        if not relevant_notifs:
            log.info("  no relevant notifications found")
            return

        log.info("{} relevant notifs found".format(len(relevant_notifs)))
        
        # filter previously seen notifications
        with self.db_sess.transaction() as xact:
            q = xact.query(Notification.notif_id).filter(
                Notification.notif_id.in_([n.notificationID for n in relevant_notifs]))
            notif_ids_seen = q.all()
        notif_ids_seen = set(n.notif_id for n in notif_ids_seen)
        relevant_notifs = [n for n in relevant_notifs if n.notificationID not in notif_ids_seen]
        if not relevant_notifs:
            log.info("  no new relevant notifications found")
            return

        log.info("{} new relevant notifs found".format(len(relevant_notifs)))

        # sort so that notifications returned from the same API call are reported
        # in order.
        relevant_notifs.sort(key=notif.sentDate)

        # enrich notifications with details
        # TODO: maybe if we fail to fetch details, drop it and pick up on the next poll? that sux though. we should do some smart retrying.
        texts = get_texts(self.api, self.token, c.character.id, [n.notificationID for n in relevant_notifs])
        log.info(texts)
        if texts is None:
            # TODO: bubble out the reason and retry later if it was a core error
            log.warn("notification text failed!")
            texts = {}

        if texts is not None:
            for notif in relevant_notifs:
                notif['text'] = texts.get(notif.notificationID, "")

        names = get_names(self.api, [n.senderID for n in relevant_notifs])
        if names is not None:
            for notif in relevant_notifs:
                notif['sender_name'] = names.get(notif.senderID)

        # write new notifications to the database!
        with self.db_sess.transaction() as xact:
            for notif in relevant_notifs:
                sent_date = datetime.strptime(notif.sentDate, '%Y-%m-%d %H:%M:%S').replace(tzinfo=utc)
                log.info("sent_date: %r", sent_date)
                n = Notification(
                    notif_id=notif.notificationID,
                    recip_id=c.character.id,
                    type=notif.typeID,
                    sender_id=notif.senderID,
                    sender_name=notif.sender_name,
                    sent_date=sent_date,
                    text=notif.text,
                )
                xact.add(n)
                # send a ping with the new max sequence_id?
                # xxx is sending orm objects across threads like this okay?
                self.ping_queue.put(n)

#!/usr/bin/env python
"""Watchtower

Usage:
    watchtower <config>
    watchtower (-h | --help)
"""


from __future__ import print_function


import ConfigParser
import logging
import logging.config
import sqlalchemy

from braveapi.client import API
from docopt import docopt
from ecdsa.keys import SigningKey, VerifyingKey
from ecdsa.curves import NIST256p
from hashlib import sha256
from six.moves import queue

from . import db
from . import model
from .pinger import Pinger
from .poller import NotificationPoller


def get_api(config):
    my_priv_key = SigningKey.from_string(config.get('core', 'app.priv_key').decode('hex'), curve=NIST256p, hashfunc=sha256)
    server_pub_key = VerifyingKey.from_string(config.get('core', 'server.pub_key').decode('hex'), curve=NIST256p, hashfunc=sha256)
    return API(config.get('core', 'server.endpoint'), config.get('core', 'app.id'), my_priv_key, server_pub_key)


def load_config(config_file):
    logging.config.fileConfig(config_file, disable_existing_loggers=False)

    config = ConfigParser.RawConfigParser()
    config.read([config_file])

    return config


def run(config_file):
    config = load_config(config_file)

    api = get_api(config)
    token = config.get('core', 'app.token')
    engine = sqlalchemy.create_engine(config.get('db', 'sqlalchemy.uri'))
    Session = db.sessionmaker(bind=engine)

    relevant_alliances = set(config.get('watchtower', 'relevant_alliances').split(', '))

    info = api.core.info(token=token)
    def care_about_character(c):
        alliance = c.alliance.name if c.alliance else None
        return alliance in relevant_alliances
    characters = [c for c in info.characters if care_about_character(c)]

    ping_q = queue.Queue()
    # Pinger gets a fresh api object because I don't trust it to be thread safe
    # (though it probably would be fine).
    pinger = Pinger(config, get_api(config), ping_q)
    poller = NotificationPoller(api, token, Session(), characters, ping_q)

    pinger.start()
    poller.start()


def create_db(config_file):
    config = load_config(config_file)
    engine = sqlalchemy.create_engine(config.get('db', 'sqlalchemy.uri'))
    model.Base.metadata.create_all(engine)


def main():
    arguments = docopt(__doc__)
    config_file = arguments['<config>']
    run(config_file)


if __name__ == "__main__":
    main()

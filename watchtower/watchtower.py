#!/usr/bin/env python
"""Watchtower

Usage:
    watchtower <config>
    watchtower (-h | --help)
"""


import ConfigParser
import logging
import logging.config

from braveapi.client import API
from docopt import docopt

from .util import notif_name, relevant_notifs


def get_api(config):
    my_priv_key = SigningKey.from_string(config.get('core', 'app.priv_key').decode('hex'), curve=NIST256p, hashfunc=sha256)
    server_pub_key = VerifyingKey.from_string(config.get('core', 'server.pub_key').decode('hex'), curve=NIST256p, hashfunc=sha256)
    return API(config.get('core', 'app.priv_key'), config.get('core', 'app.id'), my_priv_key, server_pub_key)


def main(config):
    arguments = docopt(__doc__)

    config_file = arguments['<config>']

    logging.config.fileConfig(config_file)
    config = ConfigParser.RawConfigParser()
    config.read([config_file])

    api = get_api(config)
    info = api.core.info(token=token)
    for c in info.characters:
        alliance = c.alliance.name if c.alliance else "."
        print c.character.name, "-", alliance

        if alliance == "Of Sound Mind":
            notifs_res = api.proxy.char.notifications(token=token, characterID=c.character.id)
            for notif in notifs_res.row:
                if notif.typeID in relevant_notifs:
                    print notif.typeID, notif.notificationID, c.character.name


if __name__ == "__main__":
    main()

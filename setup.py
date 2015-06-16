#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='watchtower',
    version='0.1',
    description='Sov & Tower notification aggregator',
    packages=find_packages(),

    install_requires=[
        'alembic',
        'braveapi',
        'docopt',
        'enum34',
        'irc',
        'psycopg2',
        'requests',
        'six',
        'sqlalchemy',
        'pyyaml',
    ],
)

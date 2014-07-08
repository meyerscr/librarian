"""
sqery.py: Helpers for working with databases

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import sqlite3
from functools import wraps
from itertools import dropwhile
from contextlib import contextmanager

from . import __version__ as _version, __author__ as _author

__version__ = _version
__author__ = _author
__all__ = ()


DB = None


@contextmanager
def transaction():
    cur = DB.cursor()
    cur.execute('BEGIN')
    try:
        yield cur
        DB.commit()
    except sqlite3.OperationalError:
        DB.rollback()
        raise


def connect(db):
    """ Return database connection for database at specified path

    This function uses a global variable as cache so once it has established a
    connection, it returns the same connection object to all callers.

    :param db:  database path
    :returns:   connection object
    """
    global DB  # Yes, it's ugly, but it works for this simple module
    print('Connecting to SQLite3 database at %s' % db)
    DB = sqlite3.connect(db)


def disconnect():
    """ Disconnect from the database

    :param db:  database path
    """
    global DB  # Yes, it's ugly, but it works for this simple module
    DB.close()
    DB = None
    print("Disconnected from SQLite3 database")


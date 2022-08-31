# ZPsycopgDA/db.py - query execution
#
# Copyright (C) 2004-2010 Federico Di Gregorio  <fog@debian.org>
#
# psycopg2 is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# psycopg2 is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.

# Import modules needed by _psycopg to allow tools like py2exe to do
# their work without bothering about the module dependencies.

import logging

import psycopg2
from psycopg2 import DATETIME
from psycopg2 import NUMBER
from psycopg2 import ROWID
from psycopg2 import STRING
from psycopg2.extensions import BOOLEAN
from psycopg2.extensions import DATE
from psycopg2.extensions import INTEGER
from psycopg2.extensions import LONGINTEGER
from psycopg2.extensions import TIME
from psycopg2.extensions import TransactionRollbackError
from psycopg2.extensions import register_type

from Shared.DC.ZRDB.TM import TM
from ZODB.POSException import ConflictError

from . import pool
from .utils import SHOW_COLUMNS_SQL
from .utils import SHOW_TABLES_SQL


# the DB object, managing all the real query work

class DB(TM):

    _p_oid = _p_changed = None
    _registered = False
    _sort_key = '1'

    def __init__(self, dsn, tilevel, typecasts, enc='utf-8'):
        self.dsn = dsn
        self.tilevel = tilevel
        self.typecasts = typecasts
        if enc is None or enc == "":
            self.encoding = "utf-8"
        else:
            self.encoding = enc
        self.failures = 0
        self.calls = 0
        self.make_mappings()

    def getconn(self, init=True):
        # if init is False we are trying to get hold on an already existing
        # connection, so we avoid to (re)initialize it risking errors.
        conn = pool.getconn(self.dsn)
        if init:
            conn.set_session(isolation_level=int(self.tilevel))
            conn.set_client_encoding(self.encoding)
            for tc in self.typecasts:
                register_type(tc, conn)
        return conn

    def putconn(self, close=False):
        try:
            conn = pool.getconn(self.dsn, False)
        except AttributeError:
            pass
        pool.putconn(self.dsn, conn, close)

    def getcursor(self):
        conn = self.getconn(False)
        return conn.cursor()

    def _finish(self, *ignored):
        try:
            conn = self.getconn(False)
            conn.commit()
            self.putconn()
        except AttributeError:
            pass

    def _abort(self, *ignored):
        try:
            conn = self.getconn(False)
            conn.rollback()
            self.putconn()
        except AttributeError:
            pass

    def open(self):
        # this will create a new pool for our DSN if not already existing,
        # then get and immediately release a connection
        self.getconn()
        self.putconn()

    def close(self):
        # FIXME: if this connection is closed we flush all the pool associated
        # with the current DSN; does this makes sense?
        pool.flushpool(self.dsn)

    def make_mappings(self):
        """Generate the mappings used later by self.convert_description()."""
        self.type_mappings = {}
        for t, s in [(INTEGER, 'i'), (LONGINTEGER, 'i'), (NUMBER, 'n'),
                     (BOOLEAN, 'n'), (ROWID, 'i'),
                     (DATETIME, 'd'), (DATE, 'd'), (TIME, 'd')]:
            for v in t.values:
                self.type_mappings[v] = (t, s)

    def convert_description(self, desc, use_psycopg_types=False):
        """Convert DBAPI-2.0 description field to Zope format."""
        items = []
        for name, typ, width, ds, p, scale, null_ok in desc:
            m = self.type_mappings.get(typ, (STRING, 's'))
            items.append({
                'name': name,
                'type': use_psycopg_types and m[0] or m[1],
                'width': width,
                'precision': p,
                'scale': scale,
                'null': null_ok,
            })
        return items

    # tables and rows

    def tables(self, rdb=0, _care=('TABLE', 'VIEW')):
        self._register()
        c = self.getcursor()
        c.execute(SHOW_TABLES_SQL)
        res = []
        for name, owner, typ in c.fetchall():
            if typ in _care:
                res.append({'table_name': name,
                            'owner': owner,
                            'table_type': typ})
        self.putconn()
        return res

    def columns(self, table_name):
        self._register()
        c = self.getcursor()
        try:
            c.execute(SHOW_COLUMNS_SQL % table_name)
        except Exception:
            return ()
        res = []
        for name, c_type, short_type in c.fetchall():
            res.append({'name': name,
                        'type': c_type,
                        'owner': '',
                        'short_type': short_type})
        self.putconn()
        return res

    # query execution

    def query(self, query_string, max_rows=None, query_data=None):
        self._register()
        self.calls = self.calls+1

        desc = ()
        res = []
        nselects = 0

        c = self.getcursor()

        try:
            for qs in [x for x in query_string.split('\0') if x]:
                try:
                    if query_data:
                        c.execute(qs, query_data)
                    else:
                        c.execute(qs)
                except TransactionRollbackError:
                    # Ha, here we have to look like we are the ZODB raising
                    # conflict errrors, raising ZPublisher.Publish.Retry just
                    # doesn't work
                    logging.debug("Serialization Error, retrying transaction",
                                  exc_info=True)
                    msg = 'TransactionRollbackError from psycopg2'
                    raise ConflictError(msg)
                except psycopg2.OperationalError:
                    msg = 'Operational error on connection, closing it.'
                    logging.exception(msg)
                    try:
                        # Only close our connection
                        self.putconn(True)
                    except Exception:
                        logging.debug("Exception while closing pool",
                                      exc_info=True)
                        pass
                if c.description is not None:
                    nselects += 1
                    if c.description != desc and nselects > 1:
                        raise psycopg2.ProgrammingError(
                            'multiple selects in single query not allowed')
                    if max_rows:
                        res = c.fetchmany(max_rows)
                    else:
                        res = c.fetchall()
                    desc = c.description
            self.failures = 0

        except Exception as err:
            self._abort()
            raise err

        return self.convert_description(desc), res

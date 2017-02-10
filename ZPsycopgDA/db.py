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

from Shared.DC.ZRDB.TM import TM
from Shared.DC.ZRDB import dbi_db

from ZODB.POSException import ConflictError

import pool

import psycopg2
from psycopg2.extensions import INTEGER, LONGINTEGER, FLOAT, BOOLEAN, DATE, TIME
from psycopg2.extensions import TransactionRollbackError, register_type
from psycopg2 import NUMBER, STRING, ROWID, DATETIME 

from logging import getLogger
LOG = getLogger('ZPsycopgDA.db')

# the DB object, managing all the real query work

class DB(TM, dbi_db.DB):

    _p_oid = _p_changed = _registered = None

    def __init__(self, dsn, tilevel, typecasts, enc='utf-8',
                 autocommit=False):
        self.dsn = dsn

        # Patch JJ 2016-05-05: Using the dsn as a key for connection
        # pooling mixes connections with different transaction
        # isolation levels, leading to very confusing and dangerous
        # errors. We need a better key, consisting of all
        # variables. This key will be used by pool.py
        self.key = str((dsn, tilevel, enc, typecasts))
        
        self.tilevel = tilevel
        self.typecasts = typecasts
        if enc is None or enc == "":
            self.encoding = "utf-8"
        else:
            self.encoding = enc
        self.failures = 0
        self.calls = 0

        # Patch JJ 2017-01-27: Add an autocommit feature which commits
        # every query in this instance
        self.autocommit = autocommit
        
        self.make_mappings()

    def getconn(self, init=True):
        retries = 10 # Magic number
        while True:
            try:
                conn = self.getconn_inner(init)
                break
            except (psycopg2.OperationalError, psycopg2.InterfaceError):
                LOG.info('Connect error. Retries: %d' % retries)
                self.putconn(True)
                retries -= 1
                # DANGER: time.sleep() does not play well in multithreading.
                #import time
                #time.sleep(0.2) # Magic number
                if retries == 0:
                    raise
        return conn
    
    def getconn_inner(self, init=True):
        # if init is False we are trying to get hold on an already existing
        # connection, so we avoid to (re)initialize it risking errors.

        # Patch JJ 2016-05-05: The pool needs to know the tilevel,
        # encoding and typecasts as well.
        conn = pool.getconn(self.dsn,
                            key=self.key, tilevel=self.tilevel,
                            encoding=self.encoding, typecasts=self.typecasts)
        
        if init:
            # Patch JJ 2014-05-27: Make sure you begin a new
            # transaction.
            try:    tainted = self.rollback_tainted
            except: tainted = False
            if tainted: conn.rollback()
            else:       conn.commit()
            self.rollback_tainted = False
            
            # use set_session where available as in these versions
            # set_isolation_level generates an extra query.
            if psycopg2.__version__ >= '2.4.2':
                conn.set_session(isolation_level=int(self.tilevel))
            else:
                conn.set_isolation_level(int(self.tilevel))
            conn.set_client_encoding(self.encoding)
            for tc in self.typecasts:
                register_type(tc, conn)
        return conn

    def putconn(self, close=False):
        try:
            # Patch JJ 2016-05-05: The pool needs to know the tilevel,
            # encoding and typecasts as well.
            conn = pool.getconn(self.dsn, False,
                                key=self.key, tilevel=self.tilevel,
                                encoding=self.encoding, typecasts=self.typecasts)
        except AttributeError:
            pass
        # Patch JJ 2016-05-05: The pool needs to know the tilevel,
        # encoding and typecasts as well.
        pool.putconn(self.dsn, conn, close,
                     key=self.key, tilevel=self.tilevel,
                     encoding=self.encoding, typecasts=self.typecasts)

    def getcursor(self):
        conn = self.getconn(False)
        # Patch JJ 2016-11-03: Catch lost connection situations
        try:
            cursor = conn.cursor()
        except psycopg2.InterfaceError:
            LOG.warning('Found interface error in getcursor(). Reconnecting')
            self.putconn(True)
            conn = self.getconn(True)
            cursor = conn.cursor()
        return cursor

    def _commit(self, put_connection=False):
        try:
            conn = self.getconn(False)

            # Patch JJ 2014-05-23: Check if the connection has beed
            # tainted by one of the statements executed. If that is
            # the case, we must roll back and raise an error.

            try:    tainted = conn.rollback_tainted
            except: tainted = False

            if tainted: conn.rollback()
            else:       conn.commit()

            self.rollback_tainted = False
            if put_connection:
                self.putconn()

            if tainted:
                raise StandardError, "Tainted connection needs to be rolled back."
            
        except AttributeError:
            pass
        
    def _finish(self, *ignored):
        self._commit(put_connection=True)
            
    def _abort(self, *ignored):
        # Patch JJ 2014-05-23: Rollbacks early in the transaction
        # result in all other queries processing without error, even
        # though the transaction will be rolled back. This is a
        # general problem with Zope transactions and database
        # transactions. They do not interact correctly if SQL queries
        # are masked in try blocks.

        # There's a problem with removing the rollback completely,
        # though. Some components of Zope, specifically the "test"
        # form of ZSQLMethods, rely on bad queries being trapped in
        # "try".
        rollback = False
        try:
            conn = self.getconn(False)
            if rollback:
                conn.rollback()
            else:
                # New method: only taint the connection
                try:
                    conn.rollback()
                except psycopg2.InterfaceError:
                    LOG.error('Rollback failed, just closing connection.')
                conn.rollback_tainted = True
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
        
        # Patch JJ 2016-05-05: The pool needs to know the tilevel,
        # encoding and typecasts as well.
        pool.flushpool(self.dsn,
                       key=self.key, tilevel=self.tilevel,
                       encoding=self.encoding, typecasts=self.typecasts)

    def sortKey(self):
        return 1

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

    ## tables and rows ##

    def tables(self, rdb=0, _care=('TABLE', 'VIEW')):
        self._register()
        c = self.getcursor()
        c.execute(
            "SELECT t.tablename AS NAME, 'TABLE' AS TYPE "
            "  FROM pg_tables t WHERE tableowner <> 'postgres' "
            "UNION SELECT v.viewname AS NAME, 'VIEW' AS TYPE "
            "  FROM pg_views v WHERE viewowner <> 'postgres' "
            "UNION SELECT t.tablename AS NAME, 'SYSTEM_TABLE\' AS TYPE "
            "  FROM pg_tables t WHERE tableowner = 'postgres' "
            "UNION SELECT v.viewname AS NAME, 'SYSTEM_TABLE' AS TYPE "
            "FROM pg_views v WHERE viewowner = 'postgres'")
        res = []
        for name, typ in c.fetchall():
            if typ in _care:
                res.append({'TABLE_NAME': name, 'TABLE_TYPE': typ})
        self.putconn()
        return res

    def columns(self, table_name):
        self._register()
        c = self.getcursor()
        try:
            c.execute('SELECT * FROM "%s" WHERE 1=0' % table_name)
        except:
            return ()
        self.putconn()
        return self.convert_description(c.description, True)

    ## query execution ##

    def query(self, query_string, max_rows=None, query_data=None):
        self._register()
        self.calls = self.calls+1

        desc = ()
        res = []
        nselects = 0

        c = self.getcursor()

        try:
            retries = 10 # Magic number
            for qs in [x for x in query_string.split('\0') if x]:
                while True:
                    try:
                        #LOG.info("Trying to execute statement %s" % qs)
                        if query_data:
                            c.execute(qs, query_data)
                        else:
                            c.execute(qs)
                        if self.autocommit:
                            # LOG.info('Autocommitting %s' % qs)
                            self._commit()
                    except TransactionRollbackError, err:
                        LOG.warning('Transaction Rollback!')
                        # Patch JJ 2016-05-03: Transaction Rollbacks
                        # should not be raised as ConflictErrors, because
                        # these trigger Request Retries (up to four
                        # times!) Instead, raise the error.
                        raise err

                        # Ha, here we have to look like we are the ZODB raising conflict errrors, raising ZPublisher.Publish.Retry just doesn't work
                        #logging.debug("Serialization Error, retrying transaction", exc_info=True)
                        #raise ConflictError("TransactionRollbackError from psycopg2")

                    except psycopg2.OperationalError, err:
                        LOG.error("Operational error on connection, closing it.")
                        try:
                            # Only close our connection
                            self.putconn(True)
                        except:
                            #LOG.debug("Something went wrong when we tried to close the pool", exc_info=True)
                            pass

                        # Patch JJ 2016-11-03: And immediately reopen it
                        if retries:
                            LOG.warning("Reopening the connection, retries: %d" % retries)
                            retries -= 1
                            self.getconn(True)
                            c = self.getcursor()
                            continue
                        
                        # Patch JJ 2014-05-23: Operational errors should
                        # not be muted! This masks transaction rollbacks
                        # in a very ugly way. Instead, raise the error.
                        LOG.info('Passing through operational error')
                        raise err

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
                    
                    # No retries on subsequent queries
                    retries = 0
                    break
            self.failures = 0

        except StandardError, err:
            self._abort()
            raise err

        return self.convert_description(desc), res

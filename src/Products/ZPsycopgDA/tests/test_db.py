##############################################################################
#
# Copyright (c) 2022 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Tests for the db module
"""
import threading
import time
import unittest

import psycopg2

from ..db import DB
from ..utils import ZDATETIME
from . import DSN
from . import NO_DB_MSG
from .utils import have_test_database


class DBTests(unittest.TestCase):

    def _getTargetClass(self):
        from Products.ZPsycopgDA.db import DB
        return DB

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def _makeSimple(self):
        return self._getTargetClass()('dsn', 'tilevel', 'typecasts')

    def test_instantiation_defaults(self):
        """ Simplest instantiation with dummy values """
        db = self._makeOne('dsn', 'tilevel', 'typecasts')

        self.assertEqual(db.dsn, 'dsn')
        self.assertEqual(db.tilevel, 'tilevel')
        self.assertEqual(db.typecasts, 'typecasts')
        self.assertEqual(db.encoding, 'utf-8')
        self.assertEqual(db.failures, 0)
        self.assertEqual(db.calls, 0)

        # class-level values
        self.assertIsNone(db._p_oid)
        self.assertIsNone(db._p_changed)
        self.assertFalse(db._registered)
        self.assertEqual(db._sort_key, '1')

        # type mappings initialization
        self.assertTrue(db.type_mappings)

    def test_instantiation_nondefaults(self):
        """ Test non-default values """
        db = self._makeOne('dsn', 'tilevel', 'typecasts', enc='latin-1')
        self.assertEqual(db.encoding, 'latin-1')

        db = self._makeOne('dsn', 'tilevel', 'typecasts', enc=None)
        self.assertEqual(db.encoding, 'utf-8')

        db = self._makeOne('dsn', 'tilevel', 'typecasts', enc='')
        self.assertEqual(db.encoding, 'utf-8')

    def test_sortKey(self):
        db = self._makeOne('dsn', 'tilevel', 'typecasts')

        self.assertEqual(db.sortKey(), '1')


@unittest.skipUnless(have_test_database(), NO_DB_MSG)
class RealDBTests(unittest.TestCase):

    def setUp(self):
        self.conn = DB(DSN, tilevel=2, typecasts={})

    def tearDown(self):
        try:
            self.conn.close()
        except KeyError:
            pass

    def test_query(self):
        tablename = 'test_%s' % str(time.time()).replace('.', '')

        # Provoke an uncaught exception
        with self.assertRaises(psycopg2.errors.SyntaxError):
            self.conn.query('CREATE TABLE %s;' % tablename)

        # Successful queries
        self.conn.query('CREATE TABLE %s(id integer);' % tablename)
        self.assertEqual(self.conn.failures, 0)

        self.conn.query('INSERT INTO %s VALUES (1);' % tablename)
        self.assertEqual(self.conn.failures, 0)

        res = self.conn.query('SELECT * FROM %s' % tablename)
        self.assertEqual(self.conn.failures, 0)
        self.assertEqual(res[1], [(1,)])

        res = self.conn.query('SELECT * FROM %s' % tablename, max_rows=5)
        self.assertEqual(self.conn.failures, 0)
        self.assertEqual(res[1], [(1,)])

        # Cleanup
        self.conn.query('DROP table %s' % tablename)

    def test_tables(self):
        # Just test for any result
        self.assertTrue(self.conn.tables())

        # Restricting results to an unknown type leaves no results
        self.assertFalse(self.conn.tables(_care=('FOO', 'BAR')))

    def test_columns(self):
        # Just test for any result
        self.assertTrue(self.conn.columns('pg_tables'))

    def test_issue_142(self):
        tablename = 'test142_%s' % str(time.time()).replace('.', '')
        conn = DB(DSN, tilevel=2, typecasts={})
        conn.open()
        try:
            cur1 = self.conn.getcursor()
            cur1.execute("create table %s(id integer)" % tablename)
            cur1.close()
            cur2 = self.conn.getcursor()
            cur2.execute("insert into %s values (1)" % tablename)
            cur2.close()
            cur3 = self.conn.getcursor()
            cur3.execute("select * from %s" % tablename)
            self.assertEqual(cur3.fetchone(), (1,))
            cur3.close()
        finally:
            conn.close()

    def test_multithreaded_connection_initialization(self):
        # test connection initialization with multiple threads
        #
        # from <https://github.com/psycopg/psycopg2/pull/2>:
        # The connection initialization (transaction isolation, typecasts)
        # was only done for first connection. When there are multiple
        # threads running in parallel, connections where used which had not
        # been initialized correctly.

        typecasts = [ZDATETIME]

        def DA_connect():
            db = DB(DSN, tilevel=2, typecasts=typecasts)
            db.open()
            return db

        failures = []

        def assert_casts(conn, name):
            # connection = conn.getcursor().connection
            # See https://github.com/psycopg/psycopg2/issues/155
            connection = conn.getconn().cursor().connection
            if (connection.string_types !=
                    {1114: ZDATETIME, 1184: ZDATETIME}):
                failures.append(f'{name} fail ({connection.string_types})')

        def test_connect(name):
            assert_casts(conn1, name)

        conn1 = DA_connect()
        try:
            t1 = threading.Thread(target=test_connect, args=('t1',))
            t1.start()
            t2 = threading.Thread(target=test_connect, args=('t2',))
            t2.start()
            t1.join()
            t2.join()

            self.assertFalse(failures)
        finally:
            conn1.close()

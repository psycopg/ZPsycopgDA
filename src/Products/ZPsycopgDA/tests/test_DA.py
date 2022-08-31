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
""" Tests for the DA module
"""
import unittest

import psycopg2

from ..DA import DEFAULT_TILEVEL
from ..DA import ZDATE
from ..DA import ZDATETIME
from ..DA import ZTIME


class ConnectionTests(unittest.TestCase):

    def _getTargetClass(self):
        from Products.ZPsycopgDA.DA import Connection
        return Connection

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_instantiation_defaults(self):
        """ Simplest instantiation with dummy values """
        conn = self._makeOne('testconn', 'Test Connection', 'dbname=foo',
                             False)

        self.assertEqual(conn.getId(), 'testconn')
        self.assertFalse(conn.zdatetime)
        self.assertEqual(conn.title, 'Test Connection')
        self.assertEqual(conn.connection_string, 'dbname=foo')
        self.assertEqual(conn.tilevel, DEFAULT_TILEVEL)
        self.assertEqual(conn.encoding, 'UTF-8')

    def test_instantiation_nondefaults(self):
        """ Test non-default values """
        conn = self._makeOne('testconn', 'Test Connection', 'dbname=foo',
                             False, tilevel='1', encoding='latin-1')

        self.assertEqual(conn.tilevel, 1)
        self.assertEqual(conn.encoding, 'latin-1')

    def test_zope_factory(self):
        from OFS.Folder import Folder

        from Products.ZPsycopgDA.DA import manage_addZPsycopgConnection

        container = Folder('root')
        manage_addZPsycopgConnection(container, 'conn_id', 'Conn Title',
                                     'dbname=baz', zdatetime=True,
                                     tilevel='5', encoding='latin-15',)

        conn = container.conn_id
        self.assertEqual(conn.getId(), 'conn_id')
        self.assertEqual(conn.title, 'Conn Title')
        self.assertEqual(conn.connection_string, 'dbname=baz')
        self.assertTrue(conn.zdatetime)
        self.assertEqual(conn.tilevel, 5)
        self.assertEqual(conn.encoding, 'latin-15')

    def test_edit(self):
        conn = self._makeOne('testconn', 'Test Connection', 'dbname=foo',
                             False)
        conn.edit('Other title', 'dbname=bar', True, tilevel='3',
                  encoding='utf-16')

        self.assertTrue(conn.zdatetime)
        self.assertEqual(conn.title, 'Other title')
        self.assertEqual(conn.connection_string, 'dbname=bar')
        self.assertEqual(conn.tilevel, 3)
        self.assertEqual(conn.encoding, 'utf-16')

    def test_manage_edit(self):
        conn = self._makeOne('testconn', 'Test Connection', 'dbname=foo',
                             False)
        conn.manage_edit('Other title', 'dbname=bar', zdatetime=True,
                         tilevel='3', encoding='utf-16')

        self.assertTrue(conn.zdatetime)
        self.assertEqual(conn.title, 'Other title')
        self.assertEqual(conn.connection_string, 'dbname=bar')
        self.assertEqual(conn.tilevel, 3)
        self.assertEqual(conn.encoding, 'utf-16')

    def test_get_type_casts(self):
        conn = self._makeOne('testconn', 'Test Connection', 'dbname=foo',
                             False)

        self.assertFalse(conn.zdatetime)
        self.assertEqual(conn.get_type_casts(),
                         (psycopg2.DATETIME,
                          psycopg2.extensions.DATE,
                          psycopg2.extensions.TIME))

        conn.edit('', '', True)
        self.assertTrue(conn.zdatetime)
        self.assertEqual(conn.get_type_casts(), (ZDATETIME, ZDATE, ZTIME))
                          

#@unittest.skipUnless(have_test_database(), NO_DB_MSG)
#class RealDBTests(unittest.TestCase):
#
#    def test_issue_142(self):
#        tablename = 'test142_%s' % str(time.time()).replace('.', '')
#        conn = DB(DSN, tilevel=2, typecasts={})
#        conn.open()
#        try:
#            cur1 = conn.getcursor()
#            cur1.execute("create table %s(id integer)" % tablename)
#            cur1.close()
#            cur2 = conn.getcursor()
#            cur2.execute("insert into %s values (1)" % tablename)
#            cur2.close()
#            cur3 = conn.getcursor()
#            cur3.execute("select * from %s" % tablename)
#            self.assertEqual(cur3.fetchone(), (1,))
#            cur3.close()
#        finally:
#            conn.close()
#
#    def test_multithreaded_connection_initialization(self):
#        # test connection initialization with multiple threads
#        #
#        # from <https://github.com/psycopg/psycopg2/pull/2>:
#        # The connection initialization (transaction isolation, typecasts)
#        # was only done for first connection. When there are multiple
#        # threads running in parallel, connections where used which had not
#        # been initialized correctly.
#
#        typecasts = [ZDATETIME]
#
#        def DA_connect():
#            db = DB(DSN, tilevel=2, typecasts=typecasts)
#            db.open()
#            return db
#
#        failures = []
#
#        def assert_casts(conn, name):
#            # connection = conn.getcursor().connection
#            # See https://github.com/psycopg/psycopg2/issues/155
#            connection = conn.getconn().cursor().connection
#            if (connection.string_types !=
#                    {1114: ZDATETIME, 1184: ZDATETIME}):
#                failures.append(
#                    '%s fail (%s)' % (name, connection.string_types))
#
#        def test_connect(name):
#            assert_casts(conn1, name)
#
#        conn1 = DA_connect()
#        try:
#            t1 = threading.Thread(target=test_connect, args=('t1',))
#            t1.start()
#            t2 = threading.Thread(target=test_connect, args=('t2',))
#            t2.start()
#            t1.join()
#            t2.join()
#
#            self.assertFalse(failures)
#        finally:
#            conn1.close()

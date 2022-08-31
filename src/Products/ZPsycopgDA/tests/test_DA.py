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

from DateTime.DateTime import DateTime

from ..DA import DEFAULT_TILEVEL
from ..db import DB
from ..utils import ZDATE
from ..utils import ZDATETIME
from ..utils import ZTIME
from . import DSN
from . import NO_DB_MSG
from .utils import have_test_database


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

    def test_factory(self):
        conn = self._makeOne('testconn', 'Test Connection', 'dbname=foo',
                             False)

        self.assertIs(conn.factory(), DB)


@unittest.skipUnless(have_test_database(), NO_DB_MSG)
class RealDBTests(unittest.TestCase):

    def setUp(self):
        self.conn = self._makeOne('testconn', 'Test Connection', DSN,
                                  False, check=True)

    def _getTargetClass(self):
        from Products.ZPsycopgDA.DA import Connection
        return Connection

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_instantiation(self):
        self.assertIsInstance(self.conn._v_database_connection,
                              self.conn.factory())
        self.assertIsInstance(self.conn._v_connected, DateTime)

    def test_tpValues(self):
        # Just check for any value
        self.assertTrue(self.conn.tpValues())

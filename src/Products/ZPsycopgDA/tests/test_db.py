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
import time
import unittest

from ..db import DB
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

    def test_sortKey(self):
        db = self._makeOne('dsn', 'tilevel', 'typecasts')

        self.assertEqual(db.sortKey(), '1')


@unittest.skipUnless(have_test_database(), NO_DB_MSG)
class RealDBTests(unittest.TestCase):

    def test_issue_142(self):
        tablename = 'test142_%s' % str(time.time()).replace('.', '')
        conn = DB(DSN, tilevel=2, typecasts={})
        conn.open()
        try:
            cur1 = conn.getcursor()
            cur1.execute("create table %s(id integer)" % tablename)
            cur1.close()
            cur2 = conn.getcursor()
            cur2.execute("insert into %s values (1)" % tablename)
            cur2.close()
            cur3 = conn.getcursor()
            cur3.execute("select * from %s" % tablename)
            self.assertEqual(cur3.fetchone(), (1,))
            cur3.close()
        finally:
            conn.close()

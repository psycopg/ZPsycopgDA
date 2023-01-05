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
""" Tests for the utils module
"""
import unittest

from .dummy import COLUMNS
from .dummy import TABLE
from .dummy import FakeColumns


class UtilsTest(unittest.TestCase):

    def test__cast_DateTime(self):
        from ..utils import _cast_DateTime

        self.assertIsNone(_cast_DateTime('', None))
        self.assertEqual(_cast_DateTime('infinity', None), 'infinity')
        self.assertEqual(_cast_DateTime('-infinity', None), '-infinity')

        dt = _cast_DateTime('1999-01-08 13:05:06+01', None)
        self.assertEqual(dt.parts(), (1999, 1, 8, 13, 5, 6, 'GMT+1'))

    def test__cast_Time(self):
        from ..utils import _cast_Time

        self.assertIsNone(_cast_Time('', None))
        self.assertEqual(_cast_Time('infinity', None), 'infinity')
        self.assertEqual(_cast_Time('-infinity', None), '-infinity')

        dt = _cast_Time('16:05:00', None)
        self.assertEqual(dt.parts(),
                         (dt.year(), dt.month(), dt.day(), 16, 5, 0, 'GMT+0'))


class TableBrowserTests(unittest.TestCase):

    def _getTargetClass(self):
        from Products.ZPsycopgDA.utils import TableBrowser
        return TableBrowser

    def _makeOne(self):
        browser = self._getTargetClass()()
        browser._d = TABLE
        browser._c = FakeColumns(TABLE['table_name'])
        return browser

    def test_instantiation(self):
        browser = self._makeOne()
        self.assertEqual(browser.icon, 'what')
        self.assertEqual(browser.description(), TABLE['table_name'])
        self.assertEqual(browser.check, '')

    def test_getattr_attributeerror(self):
        browser = self._makeOne()
        with self.assertRaises(AttributeError):
            browser.unknown

    def test_getattr(self):
        browser = self._makeOne()
        self.assertEqual(browser.table_name, 'table1')

    def test_tpValues(self):
        browser = self._makeOne()
        cols = browser.tpValues()
        self.assertEqual(cols[0].table_name, 'table1')
        self.assertEqual(cols[0].icon, 'int')
        self.assertEqual(cols[1].table_name, 'table1')
        self.assertEqual(cols[1].icon, 'text')

    def test_tpId(self):
        browser = self._makeOne()
        self.assertEqual(browser.tpId(), 'table1')

    def test_tpURL(self):
        browser = self._makeOne()
        self.assertEqual(browser.tpURL(), 'Table/table1')

    def test_name(self):
        browser = self._makeOne()
        self.assertEqual(browser.name(), 'table1')

    def test_type(self):
        browser = self._makeOne()
        self.assertEqual(browser.type(), 'type1')


class ColumnBrowserTests(unittest.TestCase):

    def _getTargetClass(self):
        from Products.ZPsycopgDA.utils import ColumnBrowser
        return ColumnBrowser

    def _makeOne(self):
        browser = self._getTargetClass()()
        browser._d = COLUMNS[0]
        browser.table_name = 'table1'
        return browser

    def test_instantiation(self):
        browser = self._makeOne()
        self.assertEqual(browser.icon, 'field')

    def test_getattr_attributeerror(self):
        browser = self._makeOne()
        with self.assertRaises(AttributeError):
            browser.unknown

    def test_getattr(self):
        browser = self._makeOne()
        self.assertEqual(browser.name(), 'col1')

    def test_check(self):
        browser = self._makeOne()
        self.assertIn('table1.col1', browser.check())

    def test_tpId(self):
        browser = self._makeOne()
        self.assertEqual(browser.tpId(), 'col1')

    def test_tpURL(self):
        browser = self._makeOne()
        self.assertEqual(browser.tpURL(), 'Column/col1')

    def test_description(self):
        browser = self._makeOne()
        self.assertEqual(browser.description(), ' integer (int)')


class valuesTests(unittest.TestCase):

    def _makeOne(self):
        from Products.ZPsycopgDA.utils import values
        return values()

    def test_len(self):
        vals = self._makeOne()
        self.assertEqual(vals.len(), 1)

    def test_getitem_firstaccess(self):
        # On first access, the ``_d`` attribute is created
        vals = self._makeOne()

        def _callback():
            return ['foo', 'bar', 'baz']

        with self.assertRaises(AttributeError):
            vals._d

        vals._f = _callback
        self.assertEqual(vals[0], 'foo')

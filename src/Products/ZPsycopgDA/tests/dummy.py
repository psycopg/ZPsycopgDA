##############################################################################
#
# Copyright (c) 2001 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Dummy fixtures for testing
"""

TABLE = {'table_name': 'table1', 'table_type': 'type1', 'description': ''}

COLUMNS = [{'name': 'col1', 'description': 'desc1',
            'type': 'integer', 'short_type': 'int'},
           {'name': 'col2', 'description': 'desc2',
            'type': 'text', 'short_type': 'text'}]


class FakeColumns:

    def __init__(self, table_name):
        self.cols = {table_name: COLUMNS}

    def columns(self, table_name):
        return self.cols[table_name]

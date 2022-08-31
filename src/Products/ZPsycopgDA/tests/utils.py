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

import psycopg2

from . import DSN


def connect(dsn=DSN):
    return psycopg2.connect(dsn)


def have_test_database():
    try:
        conn = connect()
        conn.close()
        return True
    except psycopg2.OperationalError:
        # print('Connection failed with DSN: %s' % DSN)
        # import traceback
        # traceback.print_exc()
        return False

# test connection initialization with multiple threads
#
# from <https://github.com/psycopg/psycopg2/pull/2>:
# The connection initialization (transaction isolation, typecasts) was only
# done for first connection. When there are multiple threads running in
# parallel, connections where used which had not been initialized correctly.

import threading
import unittest

from ..DA import ZDATETIME
from ..db import DB
from . import DSN
from . import NO_DB_MSG
from .utils import have_test_database


@unittest.skipUnless(have_test_database(), NO_DB_MSG)
class DaThreadingTests(unittest.TestCase):
    def test_threading(self):

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
                failures.append(
                    '%s fail (%s)' % (name, connection.string_types))

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

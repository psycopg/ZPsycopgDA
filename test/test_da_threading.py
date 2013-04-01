# test connection initialization with multiple threads
#
# from <https://github.com/psycopg/psycopg2/pull/2>:
# The connection initialization (transaction isolation, typecasts) was only
# done for first connection. When there are multiple threads running in
# parallel, connections where used which had not been initialized correctly.

from Products.ZPsycopgDA.DA import ZDATETIME
from Products.ZPsycopgDA.db import DB
import threading

import testconfig

from testutils import unittest

class DaThreadingTests(unittest.TestCase):
    def test_threading(self):

        typecasts = [ZDATETIME]

        def DA_connect():
            db = DB(testconfig.dsn, tilevel=2, typecasts=typecasts)
            db.open()
            return db

        failures = []

        def assert_casts(conn, name):
            connection = conn.getcursor().connection
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

            self.assert_(not failures, failures)
        finally:
            conn1.close()

def test_suite():
    return unittest.TestLoader().loadTestsFromName(__name__)

if __name__ == "__main__":
    unittest.main()

# test reset of transaction in successive getcursor() calls
#
# issue #142 <http://psycopg.lighthouseapp.com/projects/62710/tickets/142>

from Products.ZPsycopgDA.db import DB

import testconfig
from testutils import unittest

class TransactionResetTests(unittest.TestCase):
    def test_issue_142(self):
        conn = DB(testconfig.dsn, tilevel=2, typecasts={})
        conn.open()
        try:
            cur1 = conn.getcursor()
            cur1.execute("create table test142(id integer)")
            cur1.close()
            cur2 = conn.getcursor()
            cur2.execute("insert into test142 values (1)")
            cur2.close()
            cur3 = conn.getcursor()
            cur3.execute("select * from test142")
            self.assertEquals(cur3.fetchone(), (1,))
            cur3.close()
        finally:
            conn.close()


def test_suite():
    return unittest.TestLoader().loadTestsFromName(__name__)

if __name__ == "__main__":
    unittest.main()

# test reset of transaction in successive getcursor() calls
#
# issue #142 <http://psycopg.lighthouseapp.com/projects/62710/tickets/142>

import unittest

from ..db import DB
from . import DSN
from . import NO_DB_MSG
from .utils import have_test_database


@unittest.skipUnless(have_test_database(), NO_DB_MSG)
class TransactionResetTests(unittest.TestCase):
    def test_issue_142(self):
        conn = DB(DSN, tilevel=2, typecasts={})
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
            self.assertEqual(cur3.fetchone(), (1,))
            cur3.close()
        finally:
            conn.close()

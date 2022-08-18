#!/usr/bin/env python

# psycopg2 test suite
#
# Copyright (C) 2007-2011 Federico Di Gregorio  <fog@debian.org>
#
# psycopg2 is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# In addition, as a special exception, the copyright holders give
# permission to link this program with the OpenSSL library (or with
# modified versions of OpenSSL that use the same license as OpenSSL),
# and distribute linked combinations including the two.
#
# You must obey the GNU Lesser General Public License in all respects for
# all of the code used other than OpenSSL.
#
# psycopg2 is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.

import sys
from testconfig import dsn
from testutils import unittest

def test_suite():
    # If connection to test db fails, bail out early.
    import psycopg2
    try:
        cnn = psycopg2.connect(dsn)
    except Exception, e:
        print "Failed connection to test db:", e.__class__.__name__, e
        print "Please set env vars 'PSYCOPG2_TESTDB_DSN' to valid values."
        sys.exit(1)
    else:
        cnn.close()

    suite = unittest.TestSuite()

    import test_da_threading
    suite.addTest(test_da_threading.test_suite())
    import test_xn_reset
    suite.addTest(test_xn_reset.test_suite())

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

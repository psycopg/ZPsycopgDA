# Configure the test suite from the env variables.

import os

dsn = os.environ.get('PSYCOPG2_TESTDB_DSN', 'dbname=psycopg2_test')


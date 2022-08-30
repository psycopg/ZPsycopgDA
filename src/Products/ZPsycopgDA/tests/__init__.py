import os


DEFAULT_DSN = ('user=zpsycopgdatest '
               'password=zpsycopgdatest '
               'dbname=zpsycopgdatest')
DSN = os.environ.get('ZPSYCOPGDA_TEST_DSN', DEFAULT_DSN)
NO_DB_MSG = 'Please see the documentation for running functional tests.'

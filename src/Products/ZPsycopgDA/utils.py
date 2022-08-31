""" Utility functions and classes
"""
import time
from operator import itemgetter

from psycopg2 import DATETIME
from psycopg2 import NUMBER
from psycopg2 import ROWID
from psycopg2 import STRING
from psycopg2.extensions import BOOLEAN
from psycopg2.extensions import FLOAT
from psycopg2.extensions import INTEGER
from psycopg2.extensions import new_type

from Acquisition import Implicit
from App.special_dtml import HTMLFile
from DateTime import DateTime
from ExtensionClass import Base


# zope-specific psycopg typecasters

# convert an ISO timestamp string from postgres to a Zope DateTime object
def _cast_DateTime(iso, curs):
    if iso:
        if iso in ['-infinity', 'infinity']:
            return iso
        else:
            return DateTime(iso)


# Convert a time string from postgres to a Zope DateTime object.
# NOTE: we set the day as today before feeding to DateTime so
# that it has the same DST settings.
def _cast_Time(iso, curs):
    if iso:
        if iso in ['-infinity', 'infinity']:
            return iso
        else:
            return DateTime(
                time.strftime('%Y-%m-%d %H:%M:%S',
                              time.localtime(time.time())[:3] +
                              time.strptime(iso[:8], "%H:%M:%S")[3:]))


ZDATETIME = new_type((1184, 1114), "ZDATETIME", _cast_DateTime)
ZDATE = new_type((1082,), "ZDATE", _cast_DateTime)
ZTIME = new_type((1083,), "ZTIME", _cast_Time)


# table browsing helpers

class Browser(Base):
    def __getattr__(self, name):
        try:
            return self._d[name]
        except KeyError:
            raise AttributeError(name)


class values:
    def len(self):
        return 1

    def __getitem__(self, i):
        try:
            return self._d[i]
        except AttributeError:
            pass
        self._d = self._f()
        return self._d[i]


class TableBrowser(Browser, Implicit):
    icon = 'what'
    check = ''
    info = HTMLFile('dtml/table_info', globals())
    __allow_access_to_unprotected_subobjects__ = 1

    def tpValues(self):
        v = values()
        v._f = self.tpValues_
        return v

    def tpValues_(self):
        r = []
        tname = self._d['table_name']
        for d in sorted(self._c.columns(tname), key=itemgetter('name')):
            b = ColumnBrowser()
            b._d = d
            try:
                b.icon = field_icons[d['type'].upper()]
            except Exception:
                pass
            b.table_name = tname
            r.append(b)
        return r

    def tpId(self):
        return self._d['table_name']

    def tpURL(self):
        return "Table/%s" % self._d['table_name']

    def name(self):
        return self._d['table_name']

    def type(self):
        return self._d['table_type']

    def description(self):
        return self._d['table_name']


class ColumnBrowser(Browser):
    icon = 'field'

    def check(self):
        return ('\t<input type="checkbox" name="%s.%s">' %
                (self.table_name, self._d['name']))

    def tpId(self):
        return self._d['name']

    def tpURL(self):
        return "Column/%s" % self._d['name']

    def name(self):
        return self._d['name']

    def description(self):
        return " %(type)s (%(short_type)s)" % self._d


table_icons = {
    'TABLE': 'table',
    'VIEW': 'db_view',
    'SYSTEM_TABLE': 'stable',
}

field_icons = {
    NUMBER.name: 'int',
    STRING.name: 'text',
    DATETIME.name: 'date',
    INTEGER.name: 'int',
    FLOAT.name: 'float',
    BOOLEAN.name: 'bin',
    ROWID.name: 'int',
    'TEXT': 'text',
}

SHOW_TABLES_SQL = """\
SELECT t.tablename AS name, t.tableowner AS owner, 'TABLE' AS type
  FROM pg_tables t
  WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
UNION SELECT v.viewname AS name, v.viewowner as owner, 'VIEW' AS type
  FROM pg_views v
  WHERE schemaname != 'pg_catalog'
UNION SELECT t.tablename AS name, t.tableowner AS owner, 'SYSTEM_TABLE' AS type
  FROM pg_tables t
  WHERE schemaname IN ('pg_catalog', 'information_schema')
UNION SELECT v.viewname AS name, v.viewowner as owner, 'SYSTEM_TABLE' AS type
  FROM pg_views v
  WHERE schemaname IN ('pg_catalog', 'information_schema')"""

SHOW_COLUMNS_SQL = """\
SELECT c.column_name as name, c.data_type as c_type, c.udt_name as short_type
  FROM information_schema.columns c
  WHERE table_name='%s'"""

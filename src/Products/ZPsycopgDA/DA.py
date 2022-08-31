# ZPsycopgDA/DA.py - ZPsycopgDA Zope product: Database Connection
#
# Copyright (C) 2004-2010 Federico Di Gregorio  <fog@debian.org>
#
# psycopg2 is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# psycopg2 is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.

# Import modules needed by _psycopg to allow tools like py2exe to do
# their work without bothering about the module dependencies.


from operator import itemgetter

from psycopg2 import DATETIME
from psycopg2.extensions import DATE
from psycopg2.extensions import ISOLATION_LEVEL_REPEATABLE_READ
from psycopg2.extensions import TIME

from AccessControl.class_init import InitializeClass
from AccessControl.Permissions import change_database_methods
from AccessControl.Permissions import use_database_methods
from AccessControl.Permissions import view_management_screens
from AccessControl.SecurityInfo import ClassSecurityInfo
from App.special_dtml import DTMLFile
from DateTime import DateTime
from Shared.DC.ZRDB.Connection import Connection as ConnectionBase

from .db import DB
from .utils import ZDATE
from .utils import ZDATETIME
from .utils import ZTIME
from .utils import TableBrowser
from .utils import table_icons


DEFAULT_TILEVEL = ISOLATION_LEVEL_REPEATABLE_READ

manage_addZPsycopgConnectionForm = DTMLFile('dtml/add', globals())


def manage_addZPsycopgConnection(self, id, title, connection_string,
                                 zdatetime=None, tilevel=DEFAULT_TILEVEL,
                                 encoding='', check=None, REQUEST=None):
    """Add a DB connection to a folder."""
    self._setObject(id, Connection(id, title, connection_string,
                                   zdatetime, check, tilevel, encoding))
    if REQUEST is not None:
        return self.manage_main(self, REQUEST)


class Connection(ConnectionBase):
    """ZPsycopg Connection."""
    _isAnSQLConnection = 1

    database_type = 'Psycopg2'
    meta_type = 'Z Psycopg 2 Database Connection'
    security = ClassSecurityInfo()
    zmi_icon = 'fas fa-database'
    info = None

    security.declareProtected(view_management_screens,  # NOQA: D001
                              'manage_tables')
    manage_tables = DTMLFile('dtml/tables', globals())

    security.declareProtected(view_management_screens,  # NOQA: D001
                              'manage_browse')
    manage_browse = DTMLFile('dtml/browse', globals())

    security.declareProtected(change_database_methods,  # NOQA: D001
                              'manage_properties')
    manage_properties = DTMLFile('dtml/edit', globals())
    manage_properties._setName('manage_main')
    manage_main = manage_properties

    manage_options = (ConnectionBase.manage_options[1:] +
                      ({'label': 'Browse', 'action': 'manage_browse'},))

    def __init__(self, id, title, connection_string,
                 zdatetime, check=None, tilevel=DEFAULT_TILEVEL,
                 encoding='UTF-8'):
        self.id = str(id)
        self.edit(title, connection_string, zdatetime,
                  check=check, tilevel=tilevel, encoding=encoding)

    @security.protected(use_database_methods)
    def factory(self):
        return DB

    # connection parameter editing

    @security.protected(change_database_methods)
    def edit(self, title, connection_string,
             zdatetime, check=None, tilevel=DEFAULT_TILEVEL, encoding='UTF-8'):
        self.title = title
        self.connection_string = connection_string
        self.zdatetime = zdatetime
        self.tilevel = int(tilevel)
        self.encoding = encoding

        if check:
            self.connect(self.connection_string)

    @security.protected(change_database_methods)
    def manage_edit(self, title, connection_string,
                    zdatetime=None, check=None, tilevel=DEFAULT_TILEVEL,
                    encoding='UTF-8', REQUEST=None):
        """Edit the DB connection."""
        self.edit(title, connection_string, zdatetime,
                  check=check, tilevel=tilevel, encoding=encoding)
        if REQUEST is not None:
            msg = "Connection edited."
            return self.manage_main(self, REQUEST, manage_tabs_message=msg)

    @security.protected(use_database_methods)
    def connect(self, s):
        try:
            self._v_database_connection.close()
        except Exception:
            pass

        self._v_connected = ''
        dbf = self.factory()

        # TODO: let the psycopg exception propagate, or not?
        self._v_database_connection = dbf(
            self.connection_string, self.tilevel,
            self.get_type_casts(), self.encoding)
        self._v_database_connection.open()
        self._v_connected = DateTime()

        return self

    @security.protected(use_database_methods)
    def get_type_casts(self):
        # note that in both cases order *is* important
        if self.zdatetime:
            return ZDATETIME, ZDATE, ZTIME
        else:
            return DATETIME, DATE, TIME

    @security.protected(view_management_screens)
    def tpValues(self):
        res = []
        conn = self._v_database_connection
        for d in sorted(conn.tables(rdb=0), key=itemgetter('table_name')):
            try:
                b = TableBrowser()
                b.__name__ = d['table_name']
                b._d = d
                b._c = conn
                b.icon = table_icons.get(d['table_type'], 'text')
                res.append(b)
            except Exception:
                pass
        return res


InitializeClass(Connection)

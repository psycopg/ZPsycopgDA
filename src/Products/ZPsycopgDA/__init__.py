# ZPsycopgDA/__init__.py - ZPsycopgDA Zope product
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

import os

from App.ImageFile import ImageFile

from .DA import Connection
from .DA import manage_addZPsycopgConnection
from .DA import manage_addZPsycopgConnectionForm
from .permissions import add_zpsycopgda_database_connections


def initialize(context):
    context.registerClass(
        Connection,
        permission=add_zpsycopgda_database_connections,
        constructors=(manage_addZPsycopgConnectionForm,
                      manage_addZPsycopgConnection),
        icon='icons/DBAdapterFolder_icon.gif')


misc_ = {}
for icon in ('table', 'db_view', 'stable', 'what', 'field', 'text', 'bin',
             'int', 'float', 'date', 'time', 'datetime'):
    misc_[icon] = ImageFile(os.path.join('icons', '%s.svg') % icon, globals())

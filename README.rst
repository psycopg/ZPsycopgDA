ZPsycopgDA -- psycopg2 Zope adapter
===================================

- `Project page`__
- `Download`__
- `Psycopg mailing list`__

.. __: https://github.com/psycopg/ZPsycopgDA
.. __: https://pypi.python.org/pypi/ZPsycopgDA/
.. __: http://mail.postgresql.org/mj/mj_wwwusr/domain=postgresql.org?func=lists-long-full&extra=psycopg


This is the PostgreSQL adapter for Zope 2 and 3 based on psycopg2__.

As of version 2.4.6, ZPsycopgDA has the same content of the ZPsycopgDA module
included in Psycopg 2.4.6. Future psycopg2 versions will likely not include
ZPsycopgDA, which should be installed separately.

.. __: http://initd.org/psycopg/


Prerequisites
-------------

ZPsycopgDA depends on the psycopg2 module version at least 2.4. Don't use
versions 2.4.2 or 2.4.3: they are not compatible with ZPsycopgDA. Install the
latest version available.


Installation
------------

After unpacking the archive run ``python setup.py install`` in this directory.
Alternatively use ``easy_install ZPsycopgDA`` or ``pip install ZPsycopgDA``.
The usual stuff.

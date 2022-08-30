=============
 Development
=============


Getting the source code
=======================
The source code is maintained on GitHub. To check out the trunk:

.. code-block:: sh

  $ git clone https://github.com/dataflake/Products.ZPsycopgDA.git

You can also browse the code online at
https://github.com/dataflake/Products.ZPsycopgDA


Bug tracker
===========
For bug reports, suggestions or questions please use the 
GitHub issue tracker at
https://github.com/dataflake/Products.ZPsycopgDA/issues.


Running the tests using  :mod:`zc.buildout`
===========================================
:mod:`Products.ZPsycopgDA` ships with its own :file:`buildout.cfg` file
for setting up a development buildout:

.. code-block:: sh

  $ cd Products.ZPsycopgDA
  $ python3 -m venv .
  $ bin/pip install -U pip wheel
  $ bin/pip install setuptools "zc.buildout==3.0.0rc3" tox twine
  $ bin/buildout
  ...

Once you have a buildout, the tests can be run as follows:

.. code-block:: sh

   $ bin/test 
   Running tests at level 1
   Running zope.testrunner.layer.UnitTests tests:
     Set up zope.testrunner.layer.UnitTests in 0.000 seconds.
     Running:
   ..............................................................
     Ran 62 tests with 0 failures and 0 errors in 0.043 seconds.
   Tearing down left over layers:
     Tear down zope.testrunner.layer.UnitTests in 0.000 seconds.

To run tests for all supported Python versions, code coverage and a
PEP-8 coding style checker, you can use ``tox`` after completing the
buildout step above:

.. code-block:: sh

   $ bin/tox
   GLOB sdist-make: ...
   ...
   ____________________________________ summary _____________________________________
   py27: commands succeeded
   py35: commands succeeded
   py36: commands succeeded
   py37: commands succeeded
   py38: commands succeeded
   py39: commands succeeded
   lint: commands succeeded
   coverage: commands succeeded
   congratulations :)


Running the functional tests
============================
Some tests are hard or even impossible to perform without a real running
database backend. During a normal test run they will be skipped, and
you will see output like this::

  Total: 62 tests, 0 failures, 0 errors and 5 skipped in 0.090 seconds.

To run those functional tests you need to have a PostgreSQL server
running and listening on the standard unix socket, normally
located at ``/var/run/postgresql/.s.PGSQL.5432``. This database server must
have a database named ``zpsycopgdatest`` that can be accessed by a user
``zpsycopgdatest`` with password ``zpsycopgdatest``. To set this up, log into
the running database server with an admin user and execute the following
statements::

  postgres=# CREATE USER zpsycopgdatest WITH PASSWORD 'zpsycopgdatest';
  postgres=# CREATE DATABASE zpsycopgdatest;

If everything worked you'll see test output like this::

  Total: 62 tests, 0 failures, 0 errors and 0 skipped in 0.105 seconds.


Building the documentation using :mod:`zc.buildout`
===================================================
The :mod:`Products.ZPsycopgDA` buildout installs the Sphinx 
scripts required to build the documentation, including testing 
its code snippets:

.. code-block:: sh

    $ cd docs
    $ make html
    ...
    build succeeded.

    The HTML pages are in _build/html.


Making a release
================
These instructions assume that you have a development sandbox set 
up using :mod:`zc.buildout` as the scripts used here are generated 
by the buildout.

.. code-block:: sh

  $ bin/buildout -N
  $ bin/buildout setup setup.py sdist bdist_wheel
  $ bin/twine upload -s dist/Products.ZPsycopgDA-X.X.X*

The ``bin/buildout`` step will make sure the correct package information 
is used.

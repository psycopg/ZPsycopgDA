Usage from the Zope ZMI
=======================
The database connection object can be manipulated in the :term:`Zope`
:term:`ZMI` on a series of screens, accessible through named tabs in
the main window.

Status
------
Shows the database connection status and allows the user to open or
close the connection.

Properties
----------
Edit the database connection attributes and apply any changes:

* `Title`: An optional title that shows up in the :term:`ZMI`.
* `Database Connection String`: A string encapsulating how to connect
  to the database. See :ref:`connection-string` for details.
* `Connect immediately`: Should the database connection be established
  immediately or when the first database query is run.
* `Unicode Support`: If set to ``True``, values from columns of type
  ``CHAR``, ``VARCHAR`` and ``TEXT`` are returned as unicode strings by the
  database backend.
* `Character set`: Query results will be encoded in the character set
  specified here:

  * `Not set` will emulate previous releases' behavior on Python 2, which
    used Latin-1 (ISO 8859-1), but if `Unicode results` is selected, the
    connection character set switches to UTF-8 and strings in query results
    are decoded to Unicode. On Python 3, `not set` always defaults to
    UTF-8.

  * For Python 2, you can force the character set to Latin-1 or UTF-8,
    regardless of the `Unicode results` setting. This is useful
    when your application wants to use UTF-8, but cannot deal with unicode
    return values.

  * **On Python 3, forcing the character set to Latin1 is not supported.**

* `Automatically create database`: If the `Database Connection String`
  refers to a database that does not yet exist `and` this setting is
  activated, the ZMySQLDA connector will attempt to create the
  database.

Test
----
The Test tab can be used as long as the database connection is connected.
You can enter SQL statements into the text field and view the results
sent back from the database.

Security
--------
Change the :term:`Zope` role to permission mappings here.

Undo
----
If your particular :term:`ZODB` flavor supports it, you can undo
:term:`Zope` transactions affecting the database connector object here.
These transactions don't reflect relational database transactions in the
underlying MySQL or MariaDB databases, only :term:`ZODB` transactions.

Ownership
---------
Information about the :term:`Zope` user who owns the database connector
object. Ownership in the :term:`Zope` sense confers additional rights.

Interfaces
----------
View and change the :term:`Zope` :term:`Interface` assignments for the
database connector object.

Browse
------
You can browse the database tables and columns from the relational database
specified in the connection string.

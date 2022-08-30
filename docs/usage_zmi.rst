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

* `Id` (read only): The database adapter ZODB ID.
* `Title`: An optional title that shows up in the :term:`ZMI`.
* `Database Connection String`: A string encapsulating how to connect
  to the database.
* `Connect immediately`: Should the database connection be established
  immediately or when the first database query is run.
* `Use Zope's internal DateTime`: Check this box to always convert PostgreSQL
  data/time values to instances of the Zope ``DateTime`` class.
* `Transaction isolation level`: The database transaction isolation level.
* `Encoding`: The character encoding used by the database.

Test
----
The Test tab can be used as long as the database connection is connected.
You can enter SQL statements into the text field and view the results
sent back from the database.

Security
--------
Change the :term:`Zope` role to permission mappings here.

Interfaces
----------
View and change the :term:`Zope` :term:`Interface` assignments for the
database connector object.

Browse
------
You can browse the database tables and columns from the relational database
specified in the connection string.

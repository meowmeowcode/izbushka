.. _guide:


Guide
=====

Installation
------------

First, install **izbushka**:

.. code-block:: bash

    $ pip install izbushka

Or, if you're using **poetry**:

.. code-block:: bash

    $ poetry add izbushka


Initialization
--------------

Let's imagine that in the root directory of your project you have a package named ``myapp`` and you want to put migrations inside this package. To do this, go to the root directory of the project and run this command:

.. code-block:: bash

    $ python -m izbushka myapp.migrations

It creates a configuration file named ``izbushka.yml`` and a directory ``myapp/migrations`` for migrations.


Configuration
-------------

Settings that can be configured in ``izbushka.yml``:

- ``migrations_package`` -- package with migrations
- ``host`` -- ClickHouse host to connect to, ``localhost`` by default
- ``port`` -- ClickHouse port to connect to, must be an integer value, ``8123`` by default
- ``username`` -- username for authentication on a ClickHouse server, ``Default`` by default
- ``password`` -- password for authentication on a ClickHouse server, an empty string by default
- ``database`` -- ClickHouse database to perform operations on, ``default`` by default
- ``interface`` -- ClickHouse interface to use (``http`` or ``https``), ``http`` by default
- ``cluster`` -- ClickHouse cluster

Environment variables also can be used for configuration. When set, they override the ``izbushka.yml`` settings. Here are they:

- ``CLICKHOUSE_HOST``
- ``CLICKHOUSE_PORT``
- ``CLICKHOUSE_USERNAME``
- ``CLICKHOUSE_PASSWORD``
- ``CLICKHOUSE_DATABASE``
- ``CLICKHOUSE_INTERFACE``
- ``CLICKHOUSE_CLUSTER``


About migrations
----------------

Migrations are just Python modules. Each migration must have a function named **run**.

There are three types of migrations in **izbushka**:

- **Schema migrations** to create new tables, add new columns, etc. These migrations are executed before migrations of other types.
- **Data migrations** to populate tables or move data between them. These migrations are executed after schema migrations.
- **Cleanup migrations** to drop temporary tables if they were created by other migrations and so on. Migrations of this type are last to be executed.

Migrations are joined in groups called *versions*. Each version has its own schema, data, and cleanup migrations. The order of migrations depends on the natural ordering of version names. For example, for versions named **v1** and **v2**, at first all **v1** migrations are run followed by **v2** migrations.  


Creating migrations
-------------------

Use the ``add`` command to create new migrations:

.. code-block:: bash

    $ python -m izbushka add create_events --version v1

The ``--version`` option can be omitted if it isn't the first migration. In this case, a new migration will be added to the last version:

.. code-block:: bash

    $ python -m izbushka add create_events

By default, **izbushka** creates schema migrations. Use the ``--type`` option to create data migrations:

.. code-block:: bash

    $ python -m izbushka add populate_events --type data

The same is true for cleanup migrations:

.. code-block:: bash

    $ python -m izbushka add drop_temporary_tables --type cleanup


Writing migrations
------------------

New migrations have the ``run`` function with an empty body. This function takes the ``op`` parameter with the ``Operations`` object. Use this object to execute database queries. Also, here is an import statement for the ``sql`` module that helps to build SQL queries for ClickHouse using PyPika. So, if you need to create a table with a couple of columns, a migration could look like this:

.. code-block:: python

    from izbushka import (
        Operations,
        sql,
    )


    def run(op: Operations) -> None:
        op.command(
            sql.Query.create_table("events")
            .if_not_exists()
            .columns(
                sql.Column("type", "String"),
                sql.Column("timestamp", "DateTime64(6, 'UTC')"),
            )
            .engine("MergeTree")
            .order_by("timestamp")
        )


Running migrations
------------------

Use the ``run`` command to run migrations:

.. code-block:: bash

    $ python -m izbushka run

Use the ``status`` command to check the status of migrations:

.. code-block:: bash

    $ python -m izbushka status

The ``status`` command gives an output in YAML format.


Tracking progress
-----------------

The ``status`` command can show which migrations are already done and which ones are in progress, but sometimes it's not enough, especially when you have a migration that takes a lot of time to finish. In this case, you can define the ``get_progress`` function in the migration module:

.. code-block:: python

    ...

    def get_progress(op: Operations) -> str:
        ...

The result of this function will be displayed in the ``progress`` field that will appear in the output of the ``status`` command for this migration. ``get_progress`` returns a string, so you can display almost anything -- for example, a string with a percentage of migrated data or even words like "just started" or "almost done".

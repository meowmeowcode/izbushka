.. _for_contributors:

For contributors
================

Clone the repository:

.. code-block:: bash

    git clone https://github.com/meowmeowcode/izbushka.git
    cd izbushka

Install dependencies:

.. code-block:: bash

    poetry install

Check code with MyPy:

.. code-block:: bash

    poetry run mypy

Run tests:

.. code-block:: bash

    poetry run docker-compose up -d
    poetry run py.test tests/

Autoformat code:

.. code-block:: bash

    poetry run black .

Check the coding style:

.. code-block:: bash

    poetry run black .

Generate the documentation:

.. code-block:: bash

    cd docs
    make html

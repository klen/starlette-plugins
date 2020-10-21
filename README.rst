Starlette-Plugins
#################

.. _description:

**starlette-plugins** -- A helper to make plugins faster with Starlette_

Starlette-Plugins is a helper to write plugins easier

.. _badges:

.. image:: https://github.com/klen/starlette-plugins/workflows/tests/badge.svg
    :target: https://github.com/klen/starlette-plugins/actions
    :alt: Tests Status

.. image:: https://img.shields.io/pypi/v/starlette-plugins
    :target: https://pypi.org/project/starlette-plugins/
    :alt: PYPI Version

.. _contents:

.. contents::

.. _requirements:

Requirements
=============

- python >= 3.7

.. _installation:

Installation
=============

**starlette-plugins** should be installed using pip: ::

    pip install starlette-plugins


Usage
=====

Let's imagine that we need to write Starlette plugins for Peewee ORM.

.. code:: python

    from aiopeewee import db_url

    from starlette_plugins import StarlettePlugin

    class Peewee(StarlettePlugin):

        # Give your plugin a name
        name = 'db'

        # Prepare a default configuration
        config = {
            'url': 'sqlite+async:///db.sqlite',
            'connection_params': {},
        }

    def __init__(self, app=None, **settings):
        super(Peewee, self).__init__(app, **settings)
        self.database = None

    def setup(self, app, **settings):
        """Setup the plugin."""
        super(Peewee, self).setup(app, **settings)
        self.database = db_url.connect(self.config.url, **self.config.connection_params)

    async def middleware(self, app, scope, receive, send):
        """An optional ASGI middleware."""
        async with self.database:
            await app(scope, receive, send)

    async def on_shutdown(self):
        """ The methods are supported: `on_startup`, `on_shutdown`."""
        if hasattr(self.database, 'close_all'):
            self.database.close_all()


Use the plugin

.. code:: python

   from starlette.applications import Starlette

   db = Peewee(url='postgres+async://database')
   db.setup(app)


.. _bugtracker:

Bug tracker
===========

If you have any suggestions, bug reports or
annoyances please report them to the issue tracker
at https://github.com/klen/starlette-plugins/issues

.. _contributing:

Contributing
============

Development of the project happens at: https://github.com/klen/starlette-plugins

.. _license:

License
========

Licensed under a `MIT license`_.


.. _links:

.. _klen: https://github.com/klen
.. _MIT license: http://opensource.org/licenses/MIT
.. _Starlette: https://starlette.io


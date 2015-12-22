aiodjango
=========

This is a proof-of-concept experiment to combine a Django WSGI app mixed with
async views/websocket handlers using aiohttp. The API is highly unstable
and I wouldn't recommend that you use this code for anything other than
wild experimentation.

.. image:: https://travis-ci.org/mlavin/aiodjango.svg
    :target: https://travis-ci.org/mlavin/aiodjango

.. image:: https://codecov.io/github/mlavin/aiodjango/coverage.svg?branch=master
    :target: https://codecov.io/github/mlavin/aiodjango?branch=master

.. image:: https://readthedocs.org/projects/aiodjango/badge/?version=latest
    :target: http://aiodjango.readthedocs.org/en/latest/?badge=latest
    :alt: Documentation Status


How It Works
------------

``aidjango.get_aio_application`` builds an application which combines both
request handlers/views from Django and `aiohttp.web <http://aiohttp.readthedocs.org/en/stable/web.html>`_.
Views are defined using the normal Django url pattern syntax but
any handler which is a coroutine is handled by the ``aiohttp`` application
while the rest of the views are handled by the normal Django app.

Internal this makes use of `aiohttp-wsgi <https://github.com/etianen/aiohttp-wsgi>`_
which runs the Django WSGI app in a thread-pool to minimize blocking the async
portions of the app.


Running the Demo
----------------

The example project requires Python 3.4+ to run. You should create a virtualenv
to install the necessary requirements::

    $ git clone https://github.com/mlavin/aiodjango.git
    $ cd aiodjango/
    $ mkvirtualenv aiodjango -p `which python3.4`
    (aiodjango) $ add2virtualenv .
    (aiodjango) $ cd example
    (aiodjango) $ pip install -r requirements.txt
    (aiodjango) $ python manage.py migrate
    (aiodjango) $ python manage.py runserver

This starts the server on http://localhost:8000/ with a new version of Django's
built-in runserver.


Documentation
-------------

Additional project documentation can be found on Read The Docs: https://aiodjango.readthedocs.org/

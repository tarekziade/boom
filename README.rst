.. image:: http://blog.ziade.org/boom.png

**Boom!** is a simple command line tool to send some load to a web app.

.. image:: https://img.shields.io/coveralls/tarekziade/boom.svg
    :target: https://coveralls.io/r/tarekziade/boom

.. image:: https://img.shields.io/travis/tarekziade/boom/master.svg
    :target: https://travis-ci.org/tarekziade/boom

.. image:: https://img.shields.io/pypi/v/boom.svg
    :target: https://pypi.python.org/pypi/boom

.. image:: https://img.shields.io/pypi/pyversions/boom.svg
    :target: https://pypi.python.org/pypi/boom/

.. image:: https://img.shields.io/pypi/dd/boom.svg
    :target: https://pypi.python.org/pypi/boom/

Boom! is a script you can use to quickly smoke-test your
web app deployment. If you need a more complex tool,
I'd suggest looking at `Funkload <http://funkload.nuxeo.org/>`_
or `Locust <https://github.com/locustio/locust>`_.

Boom! was specifically written to replace my Apache Bench usage,
to provide a few missing features and fix a few annoyances I had
with AB.

I have no special ambitions for this tool, and since I have not
found any tool like this in the Python-land, I wrote this one.

There are a lot of other tools out there, like Siege which
seems very popular.

However, Boom! is a good choice because it works on any platform
and is able to simulate thousands of users by using greenlets.

Installation
============

Boom! requires **Gevent** and **Requests**. If you are under Windows
I strongly recommend installing Gevent with the *xxx-win32-py2.7.exe*
installer you will find  at: https://github.com/surfly/gevent/downloads

Boom! should work with the latest versions.

If you are under Linux, installing the source version is usually a better
idea. You will need libev for Gevent.

Example under Ubuntu::

    $ sudo apt-get install libev libev-dev python-dev

Then::

    $ pip install boom


Basic usage
===========

Basic usage example: 100 queries with a maximum concurrency of
10 users::

    $ boom http://localhost:80 -c 10 -n 100
    Server Software: nginx/1.2.2
    Running 100 queries - concurrency: 10.
    Starting the load [===================================] Done

    -------- Results --------
    Successful calls        100
    Total time              0.3260 s
    Average                 0.0192 s
    Fastest                 0.0094 s
    Slowest                 0.0285 s
    Amplitude               0.0191 s
    RPS                     306
    BSI                     Pretty good

    -------- Legend --------
    RPS: Request Per Second
    BSI: Boom Speed Index


Boom! has more options::

    $ boom --help
    usage: boom [-h] [--version] [-m {GET,POST,DELETE,PUT,HEAD,OPTIONS}]
                [--content-type CONTENT_TYPE] [-D DATA] [-c CONCURRENCY] [-a AUTH]
                [--header HEADER] [--pre-hook PRE_HOOK] [--post-hook POST_HOOK]
                [--json-output] [-n REQUESTS | -d DURATION]
                [url]

    Simple HTTP Load runner.

    positional arguments:
      url                   URL to hit

    optional arguments:
      -h, --help            show this help message and exit
      --version             Displays version and exits.
      -m {GET,POST,DELETE,PUT,HEAD,OPTIONS}, --method {GET,POST,DELETE,PUT,HEAD,OPTIONS}
                            HTTP Method
      --content-type CONTENT_TYPE
                            Content-Type
      -D DATA, --data DATA  Data. Prefixed by "py:" to point a python callable.
      -c CONCURRENCY, --concurrency CONCURRENCY
                            Concurrency
      -a AUTH, --auth AUTH  Basic authentication user:password
      --header HEADER       Custom header. name:value
      --pre-hook PRE_HOOK   Python module path (eg: mymodule.pre_hook) to a
                            callable which will be executed before doing a request
                            for example: pre_hook(method, url, options). It must
                            return a tupple of parameters given in function
                            definition
      --post-hook POST_HOOK
                            Python module path (eg: mymodule.post_hook) to a
                            callable which will be executed after a request is
                            done for example: eg. post_hook(response). It must
                            return a given response parameter or raise an
                            `boom.boom.RequestException` for failed request.
      --json-output         Prints the results in JSON instead of the default
                            format
      -n REQUESTS, --requests REQUESTS
                            Number of requests
      -d DURATION, --duration DURATION
                            Duration in seconds



Design
======

Boom uses greenlets through Gevent to create *virtual users*, and uses Requests to do the
queries.

Using greenlets allows Boom to spawn large amounts of virtual users with very little
resources. It's not a problem to spawn 1000 users and hammer a web application with them.

If you are interested in this project, you are welcome to join the fun at
https://github.com/tarekziade/boom

Make sure to add yourself to the contributors list if your PR gets merged. And make sure it's in alphabetical order!

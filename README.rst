
.. image:: http://blog.ziade.org/boom.png


**Boom!** is a simple command line tool to send some load to a web app.

Boom! is a script you can use to quickly smoke-test your
web app deployment. If you need a more complex tool,
I'd suggest looking at `Funkload <http://funkload.nuxeo.org/>`_.

Boom! was specifically written to replace my Apache Bench usage,
because I was annoyed by some bugs and some stupid behaviors.

And it was **so simple** to write it, thanks to Gevent.

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
installer you will find  at: https://github.com/SiteSupport/gevent/downloads

Boom! should work with the latest 1.x version or the latest 0.x version.

If you are under Linux, installing the source version is usually a better
idea. You will need libevent for Gevent 0.x and libev for Gevent 1.x.

Example under Ubuntu::

    $ sudo apt-get install libevent python-dev

Then::

    $ pip install boom


Basic usage
===========

Basic usage example: 10 queries with a maximum concurrency of
10 users::

    $ boom http://localhost:80 -c 10 -n 10
    Server Software: nginx/1.2.2
    Running 10 times per 10 workers.
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
                [-n REQUESTS | -d DURATION]
                [url]

    Simple HTTP Load runner.

    positional arguments:
    url                   URL to hit

    optional arguments:
    -h, --help            show this help message and exit
    --version             Displays version and exits.
    -m {GET,POST,DELETE,PUT,HEAD,OPTIONS}, --method {GET,POST,DELETE,PUT,HEAD,OPTIONS}
                            Concurrency
    --content-type CONTENT_TYPE
                            Content-Type
    -D DATA, --data DATA  Data
    -c CONCURRENCY, --concurrency CONCURRENCY
                            Concurrency
    -a AUTH, --auth AUTH  Basic authentication user:password
    -n REQUESTS, --requests REQUESTS
                            Number of requests
    -d DURATION, --duration DURATION
                            Duration in seconds
    -H HEADER, --header HEADER
                            Custom header. name:value


Design
======

Boom uses greenlets through Gevent to create *virtual users*, and uses Requests to do the
queries.

Using greenlets allows Boom to spawn large amounts of virtual users with very little
resources. It's not a problem to spawn 1000 users and hammer a web application with them.

I plan to add more things like allowing people to provide a callable for the -D option.

If you are interested in this project, you are welcome to join the fun at
https://github.com/tarekziade/boom

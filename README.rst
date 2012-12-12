Boom! - Simple HTTP Load tester
===============================

**I am a prototype/experiment**


Installation::

    $ pip install boom


Basic usage example: 10 workers doign 10 queries each::

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


More options::


    $ boom --help
    usage: boom [-h] [--version] [-m {GET,POST,DELETE,PUT,HEAD}] [-c CONCURRENCY]
                [-n REQUESTS | -d DURATION]
                [url]

    AB For Humans.

    positional arguments:
    url                   URL to hit

    optional arguments:
    -h, --help            show this help message and exit
    --version             Displays version and exits.
    -m {GET,POST,DELETE,PUT,HEAD}, --method {GET,POST,DELETE,PUT,HEAD}
                            Concurrency
    -c CONCURRENCY, --concurrency CONCURRENCY
                            Concurrency
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





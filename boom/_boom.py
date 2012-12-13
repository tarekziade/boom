import logging
import argparse
import sys
import time
from collections import defaultdict
import urlparse

from gevent import monkey
import gevent
from gevent.pool import Pool
from gevent.socket import gethostbyname

monkey.patch_all()

import requests

from boom import __version__, _patch     # NOQA


logger = logging.getLogger('boom')

_stats = defaultdict(list)
_VERBS = ['GET', 'POST', 'DELETE', 'PUT', 'HEAD', 'OPTIONS']
_DATA_VERBS = ['POST', 'PUT', ]


def clear_stats():
    _stats.clear()


def print_stats(total):
    all_res = []
    for values in _stats.values():
        all_res += values

    if total == 0 or len(all_res) == 0:
        rps = avg = min_ = max_ = amp = 0
    else:
        rps = len(all_res) / total
        avg = sum(all_res) / len(all_res)
        max_ = max(all_res)
        min_ = min(all_res)
        amp = max(all_res) - min(all_res)

    print('')
    print('-------- Results --------')

    print('Successful calls\t\t%r' % len(all_res))
    print('Total time       \t\t%.4f s' % total)
    print('Average          \t\t%.4f s' % avg)
    print('Fastest          \t\t%.4f s' % min_)
    print('Slowest          \t\t%.4f s' % max_)
    print('Amplitude        \t\t%.4f s' % amp)
    print('RPS              \t\t%d' % rps)
    if rps > 500:
        print('BSI              \t\tWoooooo Fast')
    elif rps > 100:
        print('BSI              \t\tPretty good')
    elif rps > 50:
        print('BSI              \t\tMeh')
    else:
        print('BSI              \t\tHahahaha')
    print('')
    print('-------- Status codes --------')
    for code, items in _stats.items():
        print('Code %d          \t\t%d times.' % (code, len(items)))
    print('')
    print('-------- Legend --------')
    print('RPS: Request Per Second')
    print('BSI: Boom Speed Index')


def print_server_info(url, method):
    res = requests.head(url)
    print 'Server Software: ' + res.headers['server']
    print 'Running %s %s' % (method, url)


def onecall(method, url, **options):
    start = time.time()
    res = method(url, **options)
    _stats[res.status_code].append(time.time() - start)
    sys.stdout.write('=')
    sys.stdout.flush()


def run(url, num, duration, method, data, ct, auth, concurrency):

    method = getattr(requests, method.lower())
    options = {'headers': {'content-type': ct}}

    if data is not None:
        options['data'] = data

    if auth is not None:
        options['auth'] = auth.split(':', 1)

    pool = Pool(concurrency)

    if num is not None:

        for i in range(num):
            pool.spawn(onecall, method, url, **options)

        pool.join()
    else:
        with gevent.Timeout(duration, False):
            while True:
                pool.spawn(onecall, method, url, **options)

            pool.join()


def resolve(url):
    parts = urlparse.urlparse(url)
    netloc = parts.netloc.rsplit(':')
    if len(netloc) == 1:
        netloc.append('80')
    netloc = ':'.join([gethostbyname(netloc[0]), netloc[1]])
    parts = (parts.scheme, netloc) + parts[2:]
    return urlparse.urlunparse(parts)


def load(url, requests, concurrency, duration, method, data, ct, auth):
    clear_stats()
    print_server_info(url, method)
    if requests is not None:
        print('Running %d times per %d workers.' % (requests, concurrency))
    else:
        print('Running %d workers for at least %d seconds.' %
              (concurrency, duration))

    sys.stdout.write('Starting the load [')
    try:
        run(url, requests, duration, method, data, ct,
            auth, concurrency)
    finally:
        print('] Done')


def main():
    parser = argparse.ArgumentParser(description='Simple HTTP Load runner.')

    parser.add_argument('--version', action='store_true', default=False,
                        help='Displays version and exits.')

    parser.add_argument('-m', '--method', help='Concurrency',
                        type=str, default='GET', choices=_VERBS)

    parser.add_argument('--content-type', help='Content-Type',
                        type=str, default='text/plain')

    parser.add_argument('-D', '--data', help='Data', type=str)

    parser.add_argument('-c', '--concurrency', help='Concurrency',
                        type=int, default=1)

    parser.add_argument('-a', '--auth',
                        help='Basic authentication user:password', type=str)

    group = parser.add_mutually_exclusive_group()

    group.add_argument('-n', '--requests', help='Number of requests',
                       type=int)

    group.add_argument('-d', '--duration', help='Duration in seconds',
                       type=int)

    parser.add_argument('url', help='URL to hit', nargs='?')
    args = parser.parse_args()

    url = resolve(args.url)

    if args.version:
        print(__version__)
        sys.exit(0)

    if args.url is None:
        print('You need to provide an URL.')
        parser.print_usage()
        sys.exit(0)

    if args.data is not None and not args.method in _DATA_VERBS:
        print("You can't provide data with %r" % args.method)
        parser.print_usage()
        sys.exit(0)

    if args.requests is None and args.duration is None:
        args.requests = 1

    start = time.time()
    try:
        load(url, args.requests, args.concurrency, args.duration,
             args.method, args.data, args.content_type, args.auth)
    except KeyboardInterrupt:
        pass
    finally:
        total = time.time() - start
        print_stats(total)
        logger.info('Bye!')


if __name__ == '__main__':
    main()

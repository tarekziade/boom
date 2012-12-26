import logging
import argparse
import sys
import time
from collections import defaultdict
import urlparse
from copy import copy

from gevent import monkey
import gevent
from gevent.pool import Pool
from gevent.socket import gethostbyname

monkey.patch_all()

import requests

from boom import __version__, _patch     # NOQA
from boom.util import resolve_name


logger = logging.getLogger('boom')

_stats = defaultdict(list)
_VERBS = ['GET', 'POST', 'DELETE', 'PUT', 'HEAD', 'OPTIONS']
_DATA_VERBS = ['POST', 'PUT', ]


def clear_stats():
    _stats.clear()


def print_stats():
    all_res = []
    for values in _stats.values():
        all_res += values

    total = sum(all_res)

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
    print 'Server Software: %(server)s' % res.headers
    print 'Running %s %s' % (method, url)


def onecall(method, url, **options):
    start = time.time()

    if 'data' in options and callable(options['data']):
        options = copy(options)
        options['data'] = options['data'](method, url, options)

    res = method(url, **options)
    _stats[res.status_code].append(time.time() - start)
    sys.stdout.write('=')
    sys.stdout.flush()


def run(url, num=1, duration=None, method='GET', data=None, ct='text/plain',
        auth=None, concurrency=1, headers=None):

    if headers is None:
        headers = {}

    if 'content-type' not in headers:
        headers['Content-Type'] = ct

    if data is not None and data.startswith('py:'):
        callable = data[len('py:'):]
        data = resolve_name(callable)

    method = getattr(requests, method.lower())
    options = {'headers': headers}

    if data is not None:
        options['data'] = data

    if auth is not None:
        options['auth'] = tuple(auth.split(':', 1))

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
    original = netloc[0]
    resolved = gethostbyname(original)
    netloc = resolved + ':' + netloc[1]
    parts = (parts.scheme, netloc) + parts[2:]
    return urlparse.urlunparse(parts), original, resolved


def load(url, requests, concurrency, duration, method, data, ct, auth,
         headers=None):
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
            auth, concurrency, headers)
    finally:
        print('] Done')


def main():
    parser = argparse.ArgumentParser(description='Simple HTTP Load runner.')

    parser.add_argument('--version', action='store_true', default=False,
                        help='Displays version and exits.')

    parser.add_argument('-m', '--method', help='HTTP Method',
                        type=str, default='GET', choices=_VERBS)

    parser.add_argument('--content-type', help='Content-Type',
                        type=str, default='text/plain')

    parser.add_argument('-D', '--data',
                        help=('Data. Prefixed by "py:" to point '
                              'a python callable.'),
                        type=str)

    parser.add_argument('-c', '--concurrency', help='Concurrency',
                        type=int, default=1)

    parser.add_argument('-a', '--auth',
                        help='Basic authentication user:password', type=str)

    group = parser.add_mutually_exclusive_group()

    group.add_argument('-n', '--requests', help='Number of requests',
                       type=int)

    group.add_argument('-d', '--duration', help='Duration in seconds',
                       type=int)

    group.add_argument('-H', '--header', help='Custom header. name:value',
                       type=str, action='append')

    parser.add_argument('url', help='URL to hit', nargs='?')
    args = parser.parse_args()

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

    url, original, resolved = resolve(args.url)

    def _split(header):
        header = header.split(':')

        if len(header) != 2:
            print("A header must be of the form name:value")
            parser.print_usage()
            sys.exit(0)

        return header

    if args.header is None:
        headers = {}
    else:
        headers = dict([_split(header) for header in args.header])

    if original != resolved and 'Home' not in headers:
        headers['Home'] = original

    try:
        load(url, args.requests, args.concurrency, args.duration,
             args.method, args.data, args.content_type, args.auth,
             headers=headers)
    except KeyboardInterrupt:
        pass
    finally:
        print_stats()
        logger.info('Bye!')


if __name__ == '__main__':
    main()

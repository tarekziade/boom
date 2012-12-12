import logging
import argparse
import sys
import time
from collections import defaultdict

from gevent import monkey
import gevent
import requests

from boom import __version__, _patch     # NOQA


logger = logging.getLogger('boom')

_stats = defaultdict(list)


def clear_stats():
    _stats.clear()


def print_stats(total):
    all_res = []
    for values in _stats.values():
        all_res += values

    rps = len(all_res) / total
    avg = sum(all_res) / len(all_res)
    amp = max(all_res) - min(all_res)
    print('')
    print('-------- Results --------')

    print('Successful calls\t\t%r' % len(all_res))
    print('Total time       \t\t%.4f s' % total)
    print('Average          \t\t%.4f s' % avg)
    print('Fastest          \t\t%.4f s' % min(all_res))
    print('Slowest          \t\t%.4f s' % max(all_res))
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


def print_server_info(url):
    res = requests.head(url)
    print 'Server Software: ' + res.headers['server']


def onecall(url):
    start = time.time()
    try:
        res = requests.get(url)
    finally:
        _stats[res.status_code].append(time.time() - start)

    sys.stdout.write('=')
    sys.stdout.flush()


def run(url, num, duration, method='GET'):
    if num is not None:
        for i in range(num):
            onecall(url)
            gevent.sleep(0)
    else:
        start = time.time()
        while time.time() - start < duration:
            onecall(url)
            gevent.sleep(0)


def load(url, requests, concurrency, duration):
    monkey.patch_all()
    clear_stats()
    print_server_info(url)
    if requests is not None:
        print('Running %d times per %d workers.' % (requests, concurrency))
    else:
        print('Running %d workers for at least %d seconds.' %
              (concurrency, duration))

    sys.stdout.write('Starting the load [')
    try:
        jobs = [gevent.spawn(run, url, requests, duration)
                for i in range(concurrency)]
        gevent.joinall(jobs)
    finally:
        print('] Done')


def main():
    parser = argparse.ArgumentParser(description='AB For Humans.')

    parser.add_argument('--version', action='store_true', default=False,
                        help='Displays version and exits.')

    parser.add_argument('-m', '--method', help='Concurrency',
                        type=str, default='GET')

    parser.add_argument('-c', '--concurrency', help='Concurrency',
                        type=int, default=1)

    group = parser.add_mutually_exclusive_group()

    group.add_argument('-n', '--requests', help='Number of requests',
                       type=int)

    group.add_argument('-d', '--duration', help='Duration in seconds',
                       type=int)

    parser.add_argument('url', help='URL to hit', nargs='?')
    args = parser.parse_args()

    if args.version:
        print(__version__)
        sys.exit(0)

    if args.url is None:
        print('You need to provide an URL.')
        parser.print_usage()
        sys.exit(0)

    if args.requests is None and args.duration is None:
        args.requests = 1

    start = time.time()
    try:
        load(args.url, args.requests, args.concurrency, args.duration)
    except KeyboardInterrupt:
        pass
    finally:
        total = time.time() - start
        print_stats(total)
        logger.info('Bye!')


if __name__ == '__main__':
    main()

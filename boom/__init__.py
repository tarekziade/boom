import logging
import argparse
import sys
import time

from gevent import monkey
import gevent
import requests

from boom import _patch     # NOQA

logger = logging.getLogger('boom')

_stats = []


def clear_stats():
    _stats[:] = []


def print_stats(total):
    rps = len(_stats) / total
    avg = sum(_stats) / len(_stats)
    amp = max(_stats) - min(_stats)

    print('')
    print('-------- Results --------')

    print('Successful calls\t\t%r' % len(_stats))
    print('Total time       \t\t%.4f s' % total)
    print('Average          \t\t%.4f s' % avg)
    print('Fastest          \t\t%.4f s' % min(_stats))
    print('Slowest          \t\t%.4f s' % max(_stats))
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
    print('-------- Legend --------')
    print('RPS: Request Per Second')
    print('BSI: Boom Speed Index')


def print_server_info(url):
    res = requests.head(url)
    print 'Server Software: ' + res.headers['server']


def onecall(url):
    start = time.time()
    try:
        requests.get(url)
    finally:
        _stats.append(time.time() - start)

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

    parser.add_argument('-c', '--concurrency', help='Concurrency',
                        type=int, default=1)

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument('-n', '--requests', help='Number of requests',
                       type=int)

    group.add_argument('-d', '--duration', help='Duration in seconds',
                       type=int)

    parser.add_argument('url', help='URL to hit')
    args = parser.parse_args()
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

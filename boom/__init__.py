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
        print('BSI              \t\t Hahahaha')

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


def run(url, num, method='GET'):
    for i in range(num):
        onecall(url)


def load(url, requests, concurrency):
    monkey.patch_all()
    clear_stats()
    print_server_info(url)
    sys.stdout.write('Starting the load [')
    try:
        jobs = [gevent.spawn(run, url, requests) for i in range(concurrency)]
        gevent.joinall(jobs)
    finally:
        print('] Done')


def main():
    parser = argparse.ArgumentParser(description='AB For Humans.')

    parser.add_argument('-n', '--requests', help='Number of requests',
                        default=1, type=int)
    parser.add_argument('-c', '--concurrency', help='Concurrency', default=1,
                        type=int)
    parser.add_argument('url', help='URL to hit')

    args = parser.parse_args()
    start = time.time()
    try:
        load(args.url, args.requests, args.concurrency)
    except KeyboardInterrupt:
        pass
    finally:
        total = time.time() - start
        print_stats(total)
        logger.info('Bye!')


if __name__ == '__main__':
    main()

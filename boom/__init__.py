import logging
import argparse
import sys
import os
from gevent import monkey
import gevent
import urllib2
import time

logger = logging.getLogger('boom')
monkey.patch_all()

_stats = []

import requests


def clear_stats():
    _stats[:] = []


def print_stats():
    print('')
    print('Successful calls\t\t%r' % len(_stats))
    print('Average          \t\t%.4f' % (sum(_stats) / len(_stats)))
    print('Fastest          \t\t%.4f' % min(_stats))
    print('Slowest          \t\t%.4f' % max(_stats))


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
    clear_stats()
    print_server_info(url)
    sys.stdout.write('Starting the load [')
    try:
        jobs = [gevent.spawn(run, url, requests) for i in range(concurrency)]
        gevent.joinall(jobs)
    finally:
        print('] Done')

    print_stats()


def main():
    parser = argparse.ArgumentParser(description='AB For Humans.')

    parser.add_argument('-n', '--requests', help='Number of requests', default=1,
                        type=int)

    parser.add_argument('-c', '--concurrency', help='Concurrency', default=1, type=int)
    parser.add_argument('url', help='URL to hit')

    args = parser.parse_args()
    try:
        load(args.url, args.requests, args.concurrency)
    except KeyboardInterrupt:
        sys.exit(0)
    finally:
        print
        logger.info('Bye!')


if __name__ == '__main__':
    main()

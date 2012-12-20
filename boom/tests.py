import unittest
import subprocess
import sys
import shlex
import time

from gevent.pywsgi import WSGIServer
from boom._boom import run as runboom
import requests
import gevent


class App(object):
    def __init__(self):
        self.numcalls = 0

    def handle(self, env, start_response):
        if env['PATH_INFO'] == '/':
            self.numcalls +=1
            start_response('200 OK', [('Content-Type', 'text/html')])
            return ["<b>hello world</b>"]
        elif env['PATH_INFO'] == '/calls':
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return [str(self.numcalls)]
        else:
            start_response('404 Not Found', [('Content-Type', 'text/plain')])
            return ['%s' % env['PATH_INFO']]


def run():
    app = App()
    WSGIServer(('0.0.0.0', 8089), app.handle).serve_forever()


CMD = shlex.split("%s -c 'from boom.tests import run; run()'" % sys.executable)
_SERVER = None


def _start():
    global _SERVER
    print CMD
    _SERVER = subprocess.Popen(CMD)


def _stop():
    global _SERVER
    _SERVER.terminate()
    _SERVER = None


class TestBoom(unittest.TestCase):

    def setUp(self):
        _start()
        self.server = 'http://0.0.0.0:8089/'
        while True:
            try:
                requests.get(self.server)
                return
            except requests.ConnectionError:
                gevent.sleep(.1)

    def tearDown(self):
        _stop()

    def test_basic_run(self):
        runboom(self.server, num=10, concurrency=1)
        res = requests.get(self.server +'calls').content
        self.assertEqual(int(res), 10 + 1)


if __name__  == '__main__':
    run()

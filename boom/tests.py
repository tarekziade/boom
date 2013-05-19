import unittest
import subprocess
import sys
import shlex
import StringIO

from gevent.pywsgi import WSGIServer
from boom._boom import run as runboom, main
import requests
import gevent


class App(object):
    def __init__(self):
        self.numcalls = 0

    def handle(self, env, start_response):
        if env['PATH_INFO'] == '/':
            self.numcalls += 1
            start_response('200 OK', [('Content-Type', 'text/html')])
            return ["<b>hello world</b>"]
        elif env['PATH_INFO'] == '/calls':
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return [str(self.numcalls)]
        elif env['PATH_INFO'] == '/redir':
            self.numcalls += 1
            start_response('302 Found', [('Location', '/redir')])
            return []
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


def hook(method, url, options):
    options['files'] = {'file': open(__file__, 'rb')}
    return method, url, options


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
        res = requests.get(self.server + 'calls').content
        self.assertEqual(int(res), 10 + 1)

    def test_hook(self):
        runboom(self.server, method='POST', num=10, concurrency=1,
                hook='boom.tests.hook')
        res = requests.get(self.server + 'calls').content
        self.assertEqual(int(res), 10 + 1)

    def test_connection_error(self):
        errors = runboom('http://localhost:9999', num=10, concurrency=1)
        self.assertEqual(len(errors), 10)
        for error in errors:
            self.assertIsInstance(error, requests.ConnectionError)

    def test_too_many_redirects(self):
        errors = runboom(self.server + 'redir', num=2, concurrency=1)
        res = requests.get(self.server + 'calls').content
        self.assertEqual(int(res), 62 + 1)
        for error in errors:
            print error
            self.assertIsInstance(error, requests.TooManyRedirects)


class TestBoom(unittest.TestCase):

    def _run(self, *args):
        old = list(sys.argv)
        sys.argv[:] = [sys.executable] + list(args)
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        exit_code = 0
        sys.stdout = StringIO.StringIO()
        sys.stderr = StringIO.StringIO()
        try:
            main()
        except (Exception, SystemExit), e:
            if isinstance(e, SystemExit):
                exit_code = e.code
            else:
                exit_code = 1
        finally:
            sys.stdout.seek(0)
            stdout = sys.stdout.read()
            sys.stderr.seek(0)
            stderr = sys.stdout.read()
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        return exit_code, stdout, stderr

    def test_dns_resolve(self):
        code, stdout, stderr = self._run('http://that.impossiblename')
        self.assertEqual(code, 1)
        self.assertTrue('name does not exist' in stdout, stdout)


if __name__ == '__main__':
    run()

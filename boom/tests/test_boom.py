import unittest2 as unittest
import subprocess
import sys
import shlex
import StringIO
import json

from gevent.pywsgi import WSGIServer
import requests
import gevent

from boom._boom import run as runboom, main, resolve, RunResults
from boom import _boom


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
        elif env['PATH_INFO'] == '/reset':
            self.numcalls = 0
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return ['numcalls set to zero']
        else:
            start_response('404 Not Found', [('Content-Type', 'text/plain')])
            return ['%s' % env['PATH_INFO']]


def run():
    app = App()
    WSGIServer(('0.0.0.0', 8089), app.handle).serve_forever()


_CMD = "%s -c 'from boom.tests.test_boom import run; run()'"
CMD = shlex.split(_CMD % sys.executable)
_SERVER = None


def _start():
    global _SERVER
    _SERVER = subprocess.Popen(CMD, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)


def _stop():
    global _SERVER
    if _SERVER is not None:
        _SERVER.terminate()
        _SERVER = None


def hook(method, url, options):
    options['files'] = {'file': open(__file__, 'rb')}
    return method, url, options


class TestBoom(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        _start()
        cls.server = 'http://0.0.0.0:8089'
        while True:
            try:
                requests.get(cls.server + '/')
                return
            except requests.ConnectionError:
                gevent.sleep(.1)

    @classmethod
    def tearDownClass(cls):
        _stop()

    def setUp(self):
        self.get('/reset')

    def get(self, path):
        return requests.get(self.server + path)

    def test_basic_run(self):
        runboom(self.server, num=10, concurrency=1, quiet=True)
        res = self.get('/calls').content
        self.assertEqual(int(res), 10)

    def test_hook(self):
        runboom(self.server, method='POST', num=10, concurrency=1,
                hook='boom.tests.test_boom.hook', quiet=True)
        res = self.get('/calls').content
        self.assertEqual(int(res), 10)

    def test_connection_error(self):
        run_results = runboom('http://localhost:9999', num=10, concurrency=1,
                              quiet=True)
        self.assertEqual(len(run_results.errors), 10)
        for error in run_results.errors:
            self.assertIsInstance(error, requests.ConnectionError)

    def test_too_many_redirects(self):
        run_results = runboom(self.server + '/redir', num=2, concurrency=1,
                              quiet=True)
        res = self.get('/calls').content
        self.assertEqual(int(res), 62)
        for error in run_results.errors:
            self.assertIsInstance(error, requests.TooManyRedirects)

    def _run(self, *args):
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
        self.assertTrue('DNS resolution failed for' in stdout, stdout)

    def test_resolve(self):
        test_url = 'http://localhost:9999'
        url, original, resolved = resolve(test_url)
        self.assertEqual(url, 'http://127.0.0.1:9999')
        self.assertEqual(original, 'localhost')
        self.assertEqual(resolved, '127.0.0.1')

    def test_ssl_resolve(self):
        test_url = 'https://localhost:9999'
        url, original, resolved = resolve(test_url)
        self.assertEqual(url, 'https://localhost:9999')
        self.assertEqual(original, 'localhost')
        self.assertEqual(resolved, 'localhost')

    def test_resolve_no_scheme(self):
        test_url = 'http://localhost'
        url, original, resolved = resolve(test_url)
        self.assertEqual(url, 'http://127.0.0.1:80')
        self.assertEqual(original, 'localhost')
        self.assertEqual(resolved, '127.0.0.1')

    def test_resolve_no_scheme_ssl(self):
        test_url = 'https://localhost'
        url, original, resolved = resolve(test_url)
        self.assertEqual(url, 'https://localhost:443')
        self.assertEqual(original, 'localhost')
        self.assertEqual(resolved, 'localhost')

    def test_json_output(self):
        results = RunResults()
        results.status_code_counter['200'].extend([0, 0.1, 0.2])
        results.total_time = 9

        old_stdout = sys.stdout
        old_stderr = sys.stderr

        try:
            sys.stdout = StringIO.StringIO()
            sys.stderr = StringIO.StringIO()
            _boom.print_json(results)

            sys.stdout.seek(0)
            output = sys.stdout.read()
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        actual = json.loads(output)
        self.assertEqual(3, actual['count'])
        self.assertAlmostEqual(0.333, actual['rps'], delta=0.1)
        self.assertEqual(0, actual['min'])
        self.assertEqual(0.2, actual['max'])
        self.assertAlmostEqual(0.1, actual['avg'], delta=0.1)
        self.assertEqual(0.2, actual['amp'])


if __name__ == '__main__':
    run()

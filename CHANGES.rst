History
=======

1.0 - 2016-09-05
----------------

- Update `.gitignore` for pycharm users
- Alphabetize contributors list for simplicity (read OCD)
- Replace BSI response of Hahahaha with sadface
- Add Travis CI
- Add Coveralls
- Update tox to test for 2.7 and 3.5 locally (travis ci handles the rest)


0.9 - 2016-08-28
----------------

- python 3 support
- removal of python 2.6 support
- fix unittest2 dep
- Added --validator option for validating request response data
- Change --hook to --pre-hook
- added new option --post-hook for validating request response data
- fixed the error handling of failed DNS resolution
- Replace urlparse.urlparse with urllib3's parse_url


0.8 - 2013-07-14
----------------

- Nicer progress bar
- Added the --json-output option
- Integrated Tox
- Make sure the DNS resolution works with gevent 0.x and 1.x
- Improved tests
- Removed the globals


0.7 - 2013-05-21
----------------

- fixed the TypeError on empty stats - #19
- catch the dns error and display it nicely
- added SSL support - #17
- added clean error display - #16

No notes on earlier releases.

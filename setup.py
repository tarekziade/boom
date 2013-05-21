from setuptools import setup, find_packages
from boom import __version__


install_requires = ['gevent', 'requests']

try:
    import argparse     # NOQA
except ImportError:
    install_requires.append('argparse')


description = ''

for file_ in ('README', 'CHANGES', 'CONTRIBUTORS'):
    with open('%s.rst' % file_) as f:
        description += f.read() + '\n\n'


classifiers = ["Programming Language :: Python",
               "License :: OSI Approved :: Apache Software License",
               "Development Status :: 1 - Planning"]


setup(name='boom',
      version=__version__,
      url='https://github.com/tarekziade/boom',
      packages=find_packages(),
      long_description=description,
      description=("Simple HTTP Load tester"),
      author="Tarek Ziade",
      author_email="tarek@ziade.org",
      include_package_data=True,
      zip_safe=False,
      classifiers=classifiers,
      install_requires=install_requires,
      entry_points="""
      [console_scripts]
      boom = boom._boom:main
      """)

from setuptools import setup, find_packages

install_requires = ['gevent', 'requests']

try:
    import argparse     # NOQA
except ImportError:
    install_requires.append('argparse')


with open('README.rst') as f:
    README = f.read()


classifiers = ["Programming Language :: Python",
               "License :: OSI Approved :: Apache Software License",
               "Development Status :: 1 - Planning"]


setup(name='boom',
      version='0.1.1',
      url='https://github.com/tarekziade/boom',
      packages=find_packages(),
      description=("Simple HTTP Load tester"),
      author="Tarek Ziade",
      author_email="tarek@ziade.org",
      include_package_data=True,
      zip_safe=False,
      classifiers=classifiers,
      install_requires=install_requires,
      entry_points="""
      [console_scripts]
      boom = boom:main
      """)

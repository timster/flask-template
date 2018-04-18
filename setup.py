import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand


requirements = [
    'flask==0.11.1',
    'flask-cors==3.0.2',
    'flask-mail==0.9.1',
    'flask-httpauth==3.2.1',
    'peewee==2.8.5',
    'peewee-moves==1.6.1',
    'peewee-validates==0.5.0',
    'markdown==2.6.7',
]

dev_requirements = [
    'sphinx==1.7.2',
]

test_requirements = [
    'pytest==3.0.5',
    'pytest-cov==2.4.0',
    'pytest-mock==1.5.0',
]


class PyTest(TestCommand):
    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name='flaskapi',
    packages=['flaskapi'],
    author='Tim Shaffer',
    version='1.0.0',
    include_package_data=True,
    install_requires=requirements,
    tests_require=test_requirements,
    extras_require={'test': test_requirements, 'dev': dev_requirements},
    test_suite='tests',
    cmdclass={'test': PyTest},
)

import sys
from pip.download import PipSession
from pip.req import parse_requirements
from setuptools import setup
from setuptools.command.test import test as TestCommand


def get_requirements(filename):
    requirements = parse_requirements(filename, session=PipSession())
    return list(str(req.req) for req in requirements)


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
    install_requires=get_requirements('requirements.txt'),
    tests_require=get_requirements('requirements-test.txt'),
    test_suite='tests',
    cmdclass={'test': PyTest},
)

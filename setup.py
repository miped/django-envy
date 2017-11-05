import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand  # noqa

import envy


with open('README.rst') as readme:
    long_description = readme.read().strip()


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ''

    def run_tests(self):
        import pytest
        import shlex
        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


setup(
    name="django-envy",
    version=envy.__version__,
    description="Opinionated environment variable parser for Django",
    long_description=long_description,
    keywords="django, environment, env, settings, configuration",
    author="Michael Pedersen <mp@miped.dk>",
    author_email="mp@miped.dk",
    url="https://github.com/miped/django-envy/",
    license="MIT",
    py_modules=["envy"],
    tests_require=['pytest'],
    cmdclass={
        'test': PyTest
    },
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        'License :: OSI Approved :: MIT License',
        "Environment :: Web Environment",
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Framework :: Django",
        "Framework :: Django :: 1.8",
        "Framework :: Django :: 1.9",
        "Framework :: Django :: 1.10",
        "Framework :: Django :: 1.11"
    ],
)

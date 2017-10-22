django-envy
===========

An opinionated environment variable parser, which can be used with Django or standalone.

|build| |coverage| |license|

Documentation
-------------

Coming Soon


Installation
------------

Install from PyPI with pip::

    $ pip install django-envy


Usage
-----

Use envy to read and cast environment variables in your django settings:

.. code-block:: python

    from envy import env

    DEBUG = env.bool('DEBUG', default=False)  # True if os.environ['DEBUG'] == 'true', defaults to False
    TEMPLATE_DEBUG = DEBUG

    SECRET_KEY = env('SECRET_KEY')  # Will raise ImproperlyConfigured if SECRET_KEY is not in os.environ



.. |pypi| image:: https://img.shields.io/pypi/v/django-envy.svg
    :target: https://pypi.python.org/pypi/django-envy
    :alt: Latest version released on PyPi

.. |build| image:: https://img.shields.io/travis/miped/django-envy/master.svg
    :target: https://travis-ci.org/miped/django-envy
    :alt: Build status of the master branch

.. |docs| image:: https://img.shields.io/readthedocs/django-envy/stable.svg
    :target: https://django-envy.rtfd.io
    :alt: Build status of documentation

.. |coverage| image:: https://img.shields.io/codecov/c/github/miped/django-envy/master.svg
    :target: https://codecov.io/gh/miped/django-envy
    :alt: Code coverage of the master branch

.. |license| image:: https://img.shields.io/github/license/miped/django-envy.svg
    :target: https://raw.githubusercontent.com/miped/django-envy/master/LICENSE.txt
    :alt: Package license

.. _LICENSE_FILE: https://github.com/miped/django-envy/blob/master/LICENSE.txt

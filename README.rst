django-envy
===========

An opinionated environment variable parser, which focuses on strictness, and doing one thing well. Can be used standalone or with Django.

|build| |coverage| |license|


Why another environment parser?
-------------------------------

Coming Soon


Documentation
-------------

Coming Soon


Installation
------------

Install from PyPI with pip::

    $ pip install django-envy


Usage
-----

Use django-envy to read and cast environment variables in your django settings:

.. code-block:: python

    from envy import env

    DEBUG = env.bool('DEBUG', default=False)  # True if os.environ['DEBUG'] == 'true', defaults to False
    TEMPLATE_DEBUG = DEBUG

    SECRET_KEY = env('SECRET_KEY')  # Will raise ImproperlyConfigured if SECRET_KEY is not in os.environ


License
-------

Django-envy is licensed under the MIT license. See `LICENSE.txt`_


Release History
---------------

See `CHANGELOG.rst`_


Acknowledgments
---------------

Django-envy takes inspiration from multiple sources and packages:

- `12factor`_
- `12factor-django`_
- `Two Scoops of Django`_
- `rconradharris`_ / `envparse`_
- `joke2k`_ / `django-environ`_

.. _rconradharris: https://github.com/rconradharris
.. _envparse: https://github.com/rconradharris/envparse
.. _joke2k: https://github.com/joke2k
.. _django-environ: https://github.com/joke2k/django-environ
.. _12factor: http://www.12factor.net/
.. _12factor-django: http://www.wellfireinteractive.com/blog/easier-12-factor-django/
.. _`Two Scoops of Django`: http://twoscoopspress.org/

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

.. _LICENSE.txt: https://github.com/miped/django-envy/blob/master/LICENSE.txt

.. _CHANGELOG.rst: https://github.com/miped/django-envy/blob/master/CHANGELOG.rst

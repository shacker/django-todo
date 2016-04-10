============================
django todo |latest-version|
============================

|build-status| |health| |downloads| |license|

django-todo is a pluggable multi-user, multi-group task management and
assignment application for Django. It can serve as anything from a personal
to-do system to a complete, working ticketing system for organizations.

Documentation
=============

For documentation, see the django-todo wiki pages:

- `Overview and screenshots
  <http://github.com/shacker/django-todo/wiki/Overview-and-screenshots>`_

- `Requirements and installation
  <http://github.com/shacker/django-todo/wiki/Requirements-and-Installation>`_

- `Version history
  <http://github.com/shacker/django-todo/wiki/Version-history>`_

Tests
=====

Serious tests are missing, but we're checking PEP8 conformity of our syntax on
both Python 2 and 3 using ``tox``.  You can run the tests locally via::

    $ python setup.py test

No prerequisites are required, all test dependencies will be installed
automatically by ``tox`` in virtual environments created on the fly.
Unfortunately, you'll have to install ``virtualenv`` for this to work, though.

To remove all build files and folders including Python byte code you can run::

    $ python setup.py clean


.. |latest-version| image:: https://img.shields.io/pypi/v/django-todo.svg
   :alt: Latest version on PyPI
   :target: https://pypi.python.org/pypi/django-todo
.. |build-status| image:: https://travis-ci.org/shacker/django-todo.svg
   :alt: Build status
   :target: https://travis-ci.org/shacker/django-todo
.. |health| image:: https://landscape.io/github/shacker/django-todo/master/landscape.svg?style=flat
   :target: https://landscape.io/github/shacker/django-todo/master
   :alt: Code health
.. |downloads| image:: https://img.shields.io/pypi/dm/django-todo.svg
   :alt: Monthly downloads from PyPI
   :target: https://pypi.python.org/pypi/django-todo
.. |license| image:: https://img.shields.io/pypi/l/django-todo.svg
   :alt: Software license
   :target: https://github.com/shacker/django-todo/blob/master/LICENSE

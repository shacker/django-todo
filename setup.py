#!/usr/bin/env python

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import shlex
import sys

import todo as package


class Tox(TestCommand):
    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import tox
        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
        errno = tox.cmdline(args=args)
        sys.exit(errno)

setup(
    name='django-todo',
    version=package.__version__,
    description=package.__doc__.strip(),
    author=package.__author__,
    author_email=package.__email__,
    url=package.__url__,
    license=package.__license__,
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Office/Business :: Groupware',
        'Topic :: Software Development :: Bug Tracking',
    ],
    include_package_data=True,
    zip_safe=False,
    tests_require=['tox'],
    cmdclass={
        'test': Tox,
    },
)

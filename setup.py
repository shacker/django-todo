#!/usr/bin/env python

from glob import glob
from os import remove
from os.path import abspath, dirname, join
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
from shlex import split
from shutil import rmtree
from sys import exit

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
            args = split(self.tox_args)
        errno = tox.cmdline(args=args)
        exit(errno)


class Clean(TestCommand):
    def run(self):
        delete_in_root = [
            'build',
            'dist',
            '.eggs',
            '*.egg-info',
            '.tox',
        ]
        delete_everywhere = [
            '__pycache__',
            '*.pyc',
        ]
        for candidate in delete_in_root:
            rmtree_glob(candidate)
        for visible_dir in glob('[A-Za-z0-9]*'):
            for candidate in delete_everywhere:
                rmtree_glob(join(visible_dir, candidate))
                rmtree_glob(join(visible_dir, '*', candidate))
                rmtree_glob(join(visible_dir, '*', '*', candidate))


def rmtree_glob(file_glob):
    for fobj in glob(file_glob):
        try:
            rmtree(fobj)
            print('%s/ removed ...' % fobj)
        except OSError:
            try:
                remove(fobj)
                print('%s removed ...' % fobj)
            except OSError:
                pass


def read_file(*pathname):
    with open(join(dirname(abspath(__file__)), *pathname)) as f:
        return f.read()


setup(
    name='django-todo',
    version=package.__version__,
    description=package.__doc__.strip(),
    long_description=read_file('README.rst'),
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
        'clean': Clean,
        'test': Tox,
    },
)

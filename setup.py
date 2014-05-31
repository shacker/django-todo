# !/usr/bin/env python
#
from setuptools import setup, find_packages
import todo

setup(
    name='django-todo',
    version=todo.__version__,
    description='A multi-user, multi-group task management and assignment system for Django.',
    author=todo.__author__,
    author_email=todo.__email__,
    url=todo.__url__,
    license=todo.__license__,
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    include_package_data=True,
    zip_safe=False,
)

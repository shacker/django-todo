#!/usr/bin/env python

from setuptools import setup, find_packages

import todo as package

setup(
    name="django-todo",
    version=package.__version__,
    description=package.__doc__.strip(),
    author=package.__author__,
    author_email=package.__email__,
    url=package.__url__,
    license=package.__license__,
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Office/Business :: Groupware",
        "Topic :: Software Development :: Bug Tracking",
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=["unidecode"],
)

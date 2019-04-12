# Based on setup.py master example at https://github.com/pypa/sampleproject/blob/master/setup.py

from io import open
from os import path

from setuptools import setup, find_packages

import todo

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="django-todo",
    version=todo.__version__,
    description="A multi-user, multi-group task management and assignment system for Django.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shacker/django-todo",
    author="Scot Hacker",
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Operating System :: OS Independent",
        "Topic :: Office/Business :: Groupware",
        "Topic :: Office/Business :: Groupware",
        "Topic :: Software Development :: Bug Tracking",
        "Topic :: Software Development :: Bug Tracking",
    ],
    keywords="lists todo bug bugs tracking",
    packages=find_packages(),  # Finds modules with an __init__.py
    include_package_data=True,  # Pulls in non-module data from MANIFEST.in
    python_requires=">=3.5",
    install_requires=["unidecode"],
    project_urls={
        "Demo Site": "http://django-todo.org",
        "Bug Reports": "https://github.com/shacker/django-todo/issues",
        "Source": "https://github.com/shacker/django-todo",
    },
)

"""
A multi-user, multi-group task management and assignment system for Django.
"""
__version__ = "2.4.10"

__author__ = "Scot Hacker"
__email__ = "shacker@birdhouse.org"

__url__ = "https://github.com/shacker/django-todo"
__license__ = "BSD License"

try:
	# if django is not installed,
	# skips check because it blocks automated installs
	import django
	from . import check
except ModuleNotFoundError:
	# this can happen during install time, if django is not installed yet!
	pass

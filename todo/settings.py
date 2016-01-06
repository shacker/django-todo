from django.conf import settings
from django.contrib.auth.models import User

def missing_defaults():
	raise AttributeError('django-todo requires settings TODO_DEFAULT_ASSIGNEE and TODO_PUBLIC_SUBMIT_REDIRECT for anonymous ticket submissions.')

STAFF_ONLY = getattr(settings, 'TODO_STAFF_ONLY', False)
DEFAULT_LIST_ID = getattr(settings, 'TODO_DEFAULT_LIST_ID', 1)
DEFAULT_ASSIGNEE = getattr(settings, 'TODO_DEFAULT_ASSIGNEE', missing_defaults)
PUBLIC_SUBMIT_REDIRECT = getattr(settings, 'TODO_PUBLIC_SUBMIT_REDIRECT', '/')

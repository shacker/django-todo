from django.conf import settings


STAFF_ONLY = getattr(settings, 'TODO_STAFF_ONLY', False)
DEFAULT_LIST_ID = getattr(settings, 'TODO_DEFAULT_LIST_ID', 1)
DEFAULT_ASSIGNEE = getattr(settings, 'TODO_DEFAULT_ASSIGNEE', None)
PUBLIC_SUBMIT_REDIRECT = getattr(settings, 'TODO_PUBLIC_SUBMIT_REDIRECT', '/')

from django.conf import settings
from django.contrib.auth.models import User


class MissingSuperuserException(Exception):
    pass

try:
    first_superuser = User.objects.filter(is_superuser=True)[0]
except:
    raise MissingSuperuserException('django-todo requires at least one superuser in the database')

STAFF_ONLY = getattr(settings, 'TODO_STAFF_ONLY', False)
DEFAULT_ASSIGNEE = getattr(settings, 'TODO_DEFAULT_ASSIGNEE', first_superuser.username)
DEFAULT_LIST_ID = getattr(settings, 'TODO_DEFAULT_LIST_ID', 1)
PUBLIC_SUBMIT_REDIRECT = getattr(settings, 'TODO_PUBLIC_SUBMIT_REDIRECT', '/')

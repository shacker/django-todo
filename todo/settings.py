from django.conf import settings
from django.contrib.auth.models import User
from todo.models import List

STAFF_ONLY = getattr(settings, 'TODO_STAFF_ONLY', False)

first_superuser = User.objects.filter(is_superuser=True)[0]
DEFAULT_ASSIGNEE = getattr(settings, 'TODO_DEFAULT_ASSIGNEE', first_superuser.username)

first_list = List.objects.first()
DEFAULT_LIST_ID = getattr(settings, 'TODO_DEFAULT_LIST_ID', first_list.id)

PUBLIC_SUBMIT_REDIRECT = getattr(settings, 'TODO_PUBLIC_SUBMIT_REDIRECT', '/')


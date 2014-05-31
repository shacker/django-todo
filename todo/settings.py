from django.conf import settings

STAFF_ONLY = getattr(settings, 'TODO_STAFF_ONLY', False)

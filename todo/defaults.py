# If a documented django-todo option is NOT configured in settings, use these values.
from django.conf import settings

TODO_ALLOW_FILE_ATTACHMENTS = (
    settings.TODO_ALLOW_FILE_ATTACHMENTS
    if hasattr(settings, "TODO_ALLOW_FILE_ATTACHMENTS")
    else True
)

TODO_LIMIT_FILE_ATTACHMENTS = (
    settings.TODO_LIMIT_FILE_ATTACHMENTS
    if hasattr(settings, "TODO_LIMIT_FILE_ATTACHMENTS")
    else [".jpg", ".gif", ".png", ".csv", ".pdf", ".zip"]
)

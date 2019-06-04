# If a documented django-todo option is NOT configured in settings, use these values.
from django.conf import settings

hash = {
    "TODO_ALLOW_FILE_ATTACHMENTS": True,
    "TODO_COMMENT_CLASSES": [],
    "TODO_DEFAULT_ASSIGNEE": None,
    "TODO_LIMIT_FILE_ATTACHMENTS": [".jpg", ".gif", ".png", ".csv", ".pdf", ".zip"],
    "TODO_MAXIMUM_ATTACHMENT_SIZE": 5000000,
    "TODO_PUBLIC_SUBMIT_REDIRECT": "/",
    "TODO_STAFF_ONLY": True,
}

# These intentionally have no defaults (user MUST set a value if their features are used):
# TODO_DEFAULT_LIST_SLUG
# TODO_MAIL_BACKENDS
# TODO_MAIL_TRACKERS


def defaults(key: str):
    """Try to get a setting from project settings.
    If empty or doesn't exist, fall back to a value from defaults hash."""

    if hasattr(settings, key):
        val = getattr(settings, key)
    else:
        val = hash.get(key)
    return val

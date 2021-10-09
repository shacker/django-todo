# If a documented django-todo option is NOT configured in settings, use these values.
from django.conf import settings
from django.contrib.auth import get_user_model

defaults = {
    "TODO_ALLOW_FILE_ATTACHMENTS": True,
    "TODO_COMMENT_CLASSES": [],
    "TODO_DEFAULT_ASSIGNEE": None,
    "TODO_LIMIT_FILE_ATTACHMENTS": [".jpg", ".gif", ".png", ".csv", ".pdf", ".zip"],
    "TODO_MAXIMUM_ATTACHMENT_SIZE": 5000000,
    "TODO_PUBLIC_SUBMIT_REDIRECT": "/",
    "TODO_STAFF_ONLY": True,
    "TODO_USER_GROUP_ATTRIBUTE": "groups",
    "TODO_GROUP_USER_ATTRIBUTE": "user_set"
}

# These intentionally have no defaults (user MUST set a value if their features are used):
# TODO_DEFAULT_LIST_SLUG
# TODO_MAIL_BACKENDS
# TODO_MAIL_TRACKERS

def setting(key: str):
    """Try to get a setting from project settings.
    If empty or doesn't exist, fall back to a value from defaults hash."""

    val = None
    if hasattr(settings, key):
        val = getattr(settings, key)
    elif key == "TODO_GROUP_USER_ATTRIBUTE":
        # This setting can be supplied explicitly in settings (above)
        # but if not, and only if TODO_USER_GROUP_ATTRIBUTE is set
        # we can infer TODO_GROUP_USER_ATTRIBUTE from it through the
        # Django relations.
        if hasattr(settings, "TODO_USER_GROUP_ATTRIBUTE"):
            """We seek the attribute with which we can access the set of users in a group.
            Django's ManyToManyRel is a little odd in that its directional sense 
            is not guranteeed and must be tested for. One of these models is User, 
            the other is the Groups model (the one group_field points to)."""
            user_model = get_user_model()
            rel = user_group_attr().rel
            return rel.field.attname if rel.model == user_model else rel.related_name
    
    if val is None and key in defaults:
        val = defaults.get(key)

    return val

def user_group_attr():
    """Returns the field in User model that contains a user's Groups.
       The default scenario returns the auth.User.groups field. 
    """
    return getattr(get_user_model(), setting("TODO_USER_GROUP_ATTRIBUTE"))

def get_group_model():
    """We seek the model that describes user groups.
    Django's ManyToManyRel is a little odd in that its directional sense 
    is not guranteeed and must be tested for. One of these models is User, 
    the other is the Groups model (the one group_field points to)  
    """
    user_model = get_user_model()
    rel = user_group_attr().rel
    return rel.related_model if rel.model == user_model else rel.model

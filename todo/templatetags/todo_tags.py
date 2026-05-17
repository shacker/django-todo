from django import template
from django.conf import settings

register = template.Library()

# enable access to settings values from within templates
@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")

from django.conf import settings
from django.core.checks import Error, register

@register()
def dal_check(app_configs, **kwargs):
    errors = []
    missing_apps = {'dal', 'dal_select2'} - set(settings.INSTALLED_APPS)
    for missing_app in missing_apps:
        errors.append(
            Error('{} needs to be in INSTALLED_APPS'.format(missing_app))
        )
    return errors

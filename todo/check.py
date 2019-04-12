from django.core.checks import Error, register

# the sole purpose of this warning is to prevent people who have
# django-autocomplete-light installed but not configured to start the app
@register()
def dal_check(app_configs, **kwargs):
    from django.conf import settings
    from todo.features import HAS_AUTOCOMPLETE

    if not HAS_AUTOCOMPLETE:
        return []

    errors = []
    missing_apps = {"dal", "dal_select2"} - set(settings.INSTALLED_APPS)
    for missing_app in missing_apps:
        errors.append(Error("{} needs to be in INSTALLED_APPS".format(missing_app)))
    return errors

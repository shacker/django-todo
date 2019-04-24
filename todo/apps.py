from django.apps import AppConfig


class TodoConfig(AppConfig):
    name = "todo"

    def ready(self):
        # Credit: https://stackoverflow.com/a/47154840/885053
        from django.conf import settings
        settings = settings._wrapped.__dict__
        settings.setdefault("TODO_TASK_MODEL", "todo.Task")

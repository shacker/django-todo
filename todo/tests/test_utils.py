from django.core import mail

from todo.defaults import defaults
from todo.models import Comment, Task
from todo.utils import send_email_to_thread_participants, send_notify_mail


def test_send_notify_mail_not_me(todo_setup, django_user_model, email_backend_setup):
    """Assign a task to someone else, mail should be sent.
    TODO: Future tests could check for email contents.
    """

    u1 = django_user_model.objects.get(username="u1")
    u2 = django_user_model.objects.get(username="u2")

    task = Task.objects.filter(created_by=u1).first()
    task.assigned_to = u2
    task.save()
    send_notify_mail(task)
    assert len(mail.outbox) == 1


def test_send_notify_mail_myself(todo_setup, django_user_model, email_backend_setup):
    """Assign a task to myself, no mail should be sent.
    """

    u1 = django_user_model.objects.get(username="u1")
    task = Task.objects.filter(created_by=u1).first()
    task.assigned_to = u1
    task.save()
    send_notify_mail(task)
    assert len(mail.outbox) == 0


def test_send_email_to_thread_participants(todo_setup, django_user_model, email_backend_setup):
    """For a given task authored by one user, add comments by two other users.
    Notification email should be sent to all three users."""

    u1 = django_user_model.objects.get(username="u1")
    task = Task.objects.filter(created_by=u1).first()

    u3 = django_user_model.objects.create_user(
        username="u3", password="zzz", email="u3@example.com"
    )
    u4 = django_user_model.objects.create_user(
        username="u4", password="zzz", email="u4@example.com"
    )
    Comment.objects.create(author=u3, task=task, body="Hello")
    Comment.objects.create(author=u4, task=task, body="Hello")

    send_email_to_thread_participants(task, "test body", u1)
    assert len(mail.outbox) == 1  # One message to multiple recipients
    assert "u1@example.com" in mail.outbox[0].recipients()
    assert "u3@example.com" in mail.outbox[0].recipients()
    assert "u4@example.com" in mail.outbox[0].recipients()


def test_defaults(settings):
    """todo's `defaults` module provides reasonable default values for unspecified settings.
    If a value is NOT set, it should be pulled from the hash in defaults.py.
    If a value IS set, it should be respected.
    n.b. TODO_STAFF_ONLY which defaults to True in the `defaults` module."""

    key = "TODO_STAFF_ONLY"

    # Setting is not set, and should default to True (the value in defaults.py)
    assert not hasattr(settings, key)
    assert defaults(key)

    # Setting is already set to True and should be respected.
    settings.TODO_STAFF_ONLY = True
    assert defaults(key)

    # Setting is already set to False and should be respected.
    settings.TODO_STAFF_ONLY = False
    assert not defaults(key)


# FIXME: Add tests for:
# Attachments: Test whether allowed, test multiple, test extensions

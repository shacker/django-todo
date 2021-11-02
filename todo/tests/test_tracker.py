import pytest

from django.core import mail

from todo.models import Task, Comment
from todo.mail.consumers import tracker_consumer
from email.message import EmailMessage


def consumer(*args, title_format="[TEST] {subject}", **kwargs):
    return tracker_consumer(
        group="Workgroup One", task_list_slug="zip", priority=1, task_title_format=title_format
    )(*args, **kwargs)


def make_message(subject, content):
    msg = EmailMessage()
    msg.set_content(content)
    msg["Subject"] = subject
    return msg


def test_tracker_task_creation(todo_setup, django_user_model):
    msg = make_message("test1 subject", "test1 content")
    msg["From"] = "test1@example.com"
    msg["Message-ID"] = "<a@example.com>"

    # test task creation
    task_count = Task.objects.count()
    consumer([msg])

    assert task_count + 1 == Task.objects.count(), "task wasn't created"
    task = Task.objects.filter(title="[TEST] test1 subject").first()
    assert task is not None, "task was created with the wrong name"

    # test thread answers
    msg = make_message("test2 subject", "test2 content")
    msg["From"] = "test1@example.com"
    msg["Message-ID"] = "<b@example.com>"
    msg["References"] = "<nope@example.com> <a@example.com>"

    task_count = Task.objects.count()
    consumer([msg])
    assert task_count == Task.objects.count(), "comment created another task"
    Comment.objects.get(
        task=task, body__contains="test2 content", email_message_id="<b@example.com>"
    )

    # test notification answer
    msg = make_message("test3 subject", "test3 content")
    msg["From"] = "test1@example.com"
    msg["Message-ID"] = "<c@example.com>"
    msg["References"] = "<thread-{}@django-todo> <unknown@example.com>".format(task.pk)

    task_count = Task.objects.count()
    consumer([msg])
    assert task_count == Task.objects.count(), "comment created another task"
    Comment.objects.get(
        task=task, body__contains="test3 content", email_message_id="<c@example.com>"
    )

def test_tracker_email_match(todo_setup, django_user_model, settings):
    """
    Ensure that a user is added to new lists when sent from registered email
    """
    settings.TODO_MAIL_USER_MAPPER = True

    u1 = django_user_model.objects.get(username="u1")

    msg = make_message("test1 subject", "test1 content")
    msg["From"] = u1.email
    msg["Message-ID"] = "<a@example.com>"

    # test task creation
    task_count = Task.objects.count()
    consumer([msg])

    assert task_count + 1 == Task.objects.count(), "task wasn't created"
    task = Task.objects.filter(title="[TEST] test1 subject").first()
    assert task is not None, "task was created with the wrong name"
    assert task.created_by == u1

    # Check no match
    msg = make_message("test2 subject", "test2 content")
    msg["From"] = "no-match-email@example.com"
    msg["Message-ID"] = "<a@example.com>"

    # test task creation
    task_count = Task.objects.count()
    consumer([msg])

    assert task_count + 1 == Task.objects.count(), "task wasn't created"
    task = Task.objects.filter(title="[TEST] test2 subject").first()
    assert task.created_by == None


def test_tracker_match_users_false(todo_setup, django_user_model, settings):
    """
    Do not match users on incoming mail if TODO_MAIL_USER_MAPPER is False
    """
    settings.TODO_MAIL_USER_MAPPER = None

    u1 = django_user_model.objects.get(username="u1")

    msg = make_message("test1 subject", "test1 content")
    msg["From"] = u1.email
    msg["Message-ID"] = "<a@example.com>"

    # test task creation
    task_count = Task.objects.count()
    consumer([msg])

    assert task_count + 1 == Task.objects.count(), "task wasn't created"
    task = Task.objects.filter(title="[TEST] test1 subject").first()
    assert task is not None, "task was created with the wrong name"
    assert task.created_by == None

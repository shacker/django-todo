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

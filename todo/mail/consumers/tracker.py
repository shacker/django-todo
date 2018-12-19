import logging

from django.db import transaction
from django.db.models import Count
from email.charset import Charset as EMailCharset
from html2text import html2text
from todo.models import Comment, Task, TaskList

logger = logging.getLogger(__name__)


def part_decode(message):
    charset = ("ascii", "ignore")
    email_charset = message.get_content_charset()
    if email_charset:
        charset = (EMailCharset(email_charset).input_charset,)

    body = message.get_payload(decode=True)
    return body.decode(*charset)


def message_find_mime(message, mime_type):
    for submessage in message.walk():
        if submessage.get_content_type() == mime_type:
            return submessage


def message_text(message):
    text_part = message_find_mime(message, "text/plain")
    if text_part is not None:
        return part_decode(text_part)

    html_part = message_find_mime(message, "text/html")
    if html_part is not None:
        return html2text(part_decode(html_part))

    return ""


def insert_message(task_list, message, priority):
    if "message-id" not in message:
        logger.warning("missing message id, ignoring message")
        return

    if "from" not in message:
        logger.warning('missing "From" header, ignoring message')
        return

    if "subject" not in message:
        logger.warning('missing "Subject" header, ignoring message')
        return

    logger.info(
        "received message:\t"
        f"[Subject: {message['subject']}]\t"
        f"[Message-ID: {message['message-id']}]\t"
        f"[To: {message['to']}]\t"
        f"[From: {message['from']}]"
    )

    message_id = message["message-id"]
    message_from = message["from"]
    text = message_text(message)

    related_messages = message.get("references", "").split()

    # find the most relevant task to add a comment on.
    # among tasks in the selected task list, find the task having the
    # most email comments the current message references
    best_task = (
        Task.objects.filter(
            task_list=task_list, comment__email_message_id__in=related_messages
        )
        .annotate(num_comments=Count("comment"))
        .order_by("-num_comments")
        .only("id")
        .first()
    )

    with transaction.atomic():
        if best_task is None:
            best_task = Task.objects.create(
                priority=priority, title=message["subject"], task_list=task_list
            )
        logger.info(f"using task: {repr(best_task)}")

        comment, comment_created = Comment.objects.get_or_create(
            task=best_task,
            email_message_id=message_id,
            defaults={"email_from": message_from, "body": text},
        )
        logger.info(f"created comment: {repr(comment)}")


def tracker_consumer(producer, group=None, task_list_slug=None, priority=1):
    task_list = TaskList.objects.get(group__name=group, slug=task_list_slug)
    for message in producer:
        try:
            insert_message(task_list, message, priority)
        except Exception:
            # ignore exceptions during insertion, in order to avoid
            logger.exception("got exception while inserting message")

import email.utils
import functools
import time
from django.conf import settings
from django.contrib.sites.models import Site
from django.core import mail
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.template.loader import render_to_string
from todo.models import Comment, Task


def staff_check(user):
    """If TODO_STAFF_ONLY is set to True, limit view access to staff users only.
        # FIXME: More granular access control is needed... but need to do it generically,
        # to satisfy all possible todo implementations.
    """

    if hasattr(settings, "TODO_STAFF_ONLY") and settings.TODO_STAFF_ONLY:
        return user.is_staff
    else:
        # If unset or False, allow all logged in users
        return True


def user_can_read_task(task, user):
    return task.task_list.group in user.groups.all() or user.is_staff


def todo_get_backend(task):
    '''returns a mail backend for some task'''
    mail_backends = getattr(settings, "TODO_MAIL_BACKENDS", None)
    if mail_backends is None:
        return None

    task_backend = mail_backends[task.task_list.slug]
    if task_backend is None:
        return None

    return task_backend


def todo_get_mailer(user, task):
    """a mailer is a (from_address, backend) pair"""
    task_backend = todo_get_backend(task)
    if task_backend is None:
        return (None, mail.get_connection)

    from_address = getattr(task_backend, "from_address")
    from_address = email.utils.formataddr((user.username, from_address))
    return (from_address, task_backend)


def todo_send_mail(user, task, subject, body, recip_list):
    '''Send an email attached to task, triggered by user'''
    references = Comment.objects.filter(task=task).only('email_message_id')
    references = (ref.email_message_id for ref in references)
    references = ' '.join(filter(bool, references))

    from_address, backend = todo_get_mailer(user, task)
    message_hash = hash((
        subject,
        body,
        from_address,
        frozenset(recip_list),
        references,
    ))

    message_id = (
        # the task_id enables attaching back notification answers
        "<notif-{task_id}."
        # the message hash / epoch pair enables deduplication
        "{message_hash:x}."
        "{epoch}@django-todo>"
    ).format(
        task_id=task.pk,
        # avoid the -hexstring case (hashes can be negative)
        message_hash=abs(message_hash),
        epoch=int(time.time())
    )

    # the thread message id is used as a common denominator between all
    # notifications for some task. This message doesn't actually exist,
    # it's just there to make threading possible
    thread_message_id = "<thread-{}@django-todo>".format(task.pk)
    references = '{} {}'.format(references, thread_message_id)

    with backend() as connection:
        message = mail.EmailMessage(
            subject,
            body,
            from_address,
            recip_list,
            [], # Bcc
            headers={
                **getattr(backend, 'headers', {}),
                'Message-ID': message_id,
                'References': references,
                'In-reply-to': thread_message_id,
            },
            connection=connection,
        )
        message.send()


def send_notify_mail(new_task):
    '''
    Send email to assignee if task is assigned to someone other than submittor.
    Unassigned tasks should not try to notify.
    '''

    if new_task.assigned_to == new_task.created_by:
        return

    current_site = Site.objects.get_current()
    subject = render_to_string("todo/email/assigned_subject.txt", {"task": new_task})
    body = render_to_string(
        "todo/email/assigned_body.txt", {"task": new_task, "site": current_site}
    )

    recip_list = [new_task.assigned_to.email]
    todo_send_mail(new_task.created_by, new_task, subject, body, recip_list)


def send_email_to_thread_participants(task, msg_body, user, subject=None):
    '''Notify all previous commentors on a Task about a new comment.'''

    current_site = Site.objects.get_current()
    email_subject = subject
    if not subject:
        subject = render_to_string(
            "todo/email/assigned_subject.txt",
            {"task": task}
        )

    email_body = render_to_string(
        "todo/email/newcomment_body.txt",
        {"task": task, "body": msg_body, "site": current_site, "user": user},
    )

    # Get all thread participants
    commenters = Comment.objects.filter(task=task)
    recip_list = set(
        ca.author.email
        for ca in commenters
        if ca.author is not None
    )
    for related_user in (task.created_by, task.assigned_to):
        if related_user is not None:
            recip_list.add(related_user.email)
    recip_list = list(m for m in recip_list if m)

    todo_send_mail(user, task, email_subject, email_body, recip_list)


def toggle_task_completed(task_id: int) -> bool:
    try:
        task = Task.objects.get(id=task_id)
        task.completed = not task.completed
        task.save()
        return True
    except Task.DoesNotExist:
        # FIXME proper log message
        print("task not found")
        return False

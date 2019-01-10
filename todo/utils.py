from django.conf import settings
from django.contrib.sites.models import Site
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


def send_notify_mail(new_task):
    # Send email to assignee if task is assigned to someone other than submittor.
    # Unassigned tasks should not try to notify.

    if not new_task.assigned_to == new_task.created_by:
        current_site = Site.objects.get_current()
        email_subject = render_to_string("todo/email/assigned_subject.txt", {"task": new_task})
        email_body = render_to_string(
            "todo/email/assigned_body.txt", {"task": new_task, "site": current_site}
        )

        send_mail(
            email_subject,
            email_body,
            new_task.created_by.email,
            [new_task.assigned_to.email],
            fail_silently=False,
        )


def send_email_to_thread_participants(task, msg_body, user, subject=None):
    # Notify all previous commentors on a Task about a new comment.

    current_site = Site.objects.get_current()
    email_subject = (
        subject if subject else render_to_string("todo/email/assigned_subject.txt", {"task": task})
    )
    email_body = render_to_string(
        "todo/email/newcomment_body.txt",
        {"task": task, "body": msg_body, "site": current_site, "user": user},
    )

    # Get list of all thread participants - everyone who has commented, plus task creator.
    commenters = Comment.objects.filter(task=task)
    recip_list = [ca.author.email for ca in commenters]
    recip_list.append(task.created_by.email)
    recip_list = list(set(recip_list))  # Eliminate duplicates

    send_mail(email_subject, email_body, task.created_by.email, recip_list, fail_silently=False)


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

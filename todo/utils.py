import datetime

from django.contrib import messages
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.template.loader import render_to_string

from todo.models import Item, TaskList, Comment


def toggle_done(request, items):
    # Check for items in the mark_done POST array. If present, change status to complete.
    for item in items:
        i = Item.objects.get(id=item)
        old_state = "completed" if i.completed else "incomplete"
        i.completed = not i.completed  # Invert the done state, either way
        new_state = "completed" if i.completed else "incomplete"
        i.completed_date = datetime.datetime.now()
        i.save()
        messages.success(request, "Item \"{i}\" changed from {o} to {n}.".format(i=i.title, o=old_state, n=new_state))


def toggle_deleted(request, deleted_items):
    # Delete selected items
    for item_id in deleted_items:
        i = Item.objects.get(id=item_id)
        messages.success(request, "Item \"{i}\" deleted.".format(i=i.title))
        i.delete()


def send_notify_mail(request, new_task):
    # Send email to assignee if task is assigned to someone other than submittor.
    # Unassigned tasks should not try to notify.

    if new_task.assigned_to:
        current_site = Site.objects.get_current()
        email_subject = render_to_string("todo/email/assigned_subject.txt", {'task': new_task})
        email_body = render_to_string(
            "todo/email/assigned_body.txt",
            {'task': new_task, 'site': current_site, })

        send_mail(
            email_subject, email_body, new_task.created_by.email,
            [new_task.assigned_to.email], fail_silently=False)


def send_email_to_thread_participants(request, task):
    # Notify all previous commentors on a Task about a new comment.

    current_site = Site.objects.get_current()
    email_subject = render_to_string("todo/email/assigned_subject.txt", {'task': task})
    email_body = render_to_string(
        "todo/email/newcomment_body.txt",
        {'task': task, 'body': request.POST['comment-body'], 'site': current_site, 'user': request.user}
    )

    # Get list of all thread participants - everyone who has commented, plus task creator.
    commenters = Comment.objects.filter(task=task)
    recip_list = [ca.author.email for ca in commenters]
    recip_list.append(task.created_by.email)
    recip_list = list(set(recip_list))  # Eliminate duplicates

    send_mail(email_subject, email_body, task.created_by.email, recip_list, fail_silently=False)

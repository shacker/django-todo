import datetime
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.core.mail import send_mail

from todo.models import Item

# Need for links in email templates
current_site = Site.objects.get_current()


def mark_done(request, done_items):
    # Check for items in the mark_done POST array. If present, change status to complete.
    for item in done_items:
        i = Item.objects.get(id=item)
        i.completed = True
        i.completed_date = datetime.datetime.now()
        i.save()
        messages.success(request, "Item \"{i}\" marked complete.".format(i=i.title))


def undo_completed_task(request, undone_items):
    # Undo: Set completed items back to incomplete
    for item in undone_items:
        i = Item.objects.get(id=item)
        i.completed = False
        i.save()
        messages.success(request, "Previously completed task \"{i}\" marked incomplete.".format(i=i.title))


def del_tasks(request, deleted_items):
    # Delete selected items
    for item_id in deleted_items:
        i = Item.objects.get(id=item_id)
        messages.success(request, "Item \"{i}\" deleted.".format(i=i.title))
        i.delete()


def send_notify_mail(request, new_task):
    # Send email
    email_subject = render_to_string("todo/email/assigned_subject.txt", {'task': new_task})
    email_body = render_to_string(
        "todo/email/assigned_body.txt",
        {'task': new_task, 'site': current_site, })
    try:
        send_mail(
            email_subject, email_body, new_task.created_by.email,
            [new_task.assigned_to.email], fail_silently=False)
    except:
        messages.error(request, "Task saved but mail not sent. Contact your administrator.")

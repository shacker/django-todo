from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string

from todo.defaults import defaults
from todo.forms import AddExternalTaskForm
from todo.models import TaskList
from todo.utils import staff_check


@login_required
@user_passes_test(staff_check)
def external_add(request) -> HttpResponse:
    """Allow authenticated users who don't have access to the rest of the ticket system to file a ticket
    in the list specified in settings (e.g. django-todo can be used a ticket filing system for a school, where
    students can file tickets without access to the rest of the todo system).

    Publicly filed tickets are unassigned unless settings.DEFAULT_ASSIGNEE exists.
    """

    if not settings.TODO_DEFAULT_LIST_SLUG:
        # We do NOT provide a default in defaults
        raise RuntimeError(
            "This feature requires TODO_DEFAULT_LIST_SLUG: in settings. See documentation."
        )

    if not TaskList.objects.filter(slug=settings.TODO_DEFAULT_LIST_SLUG).exists():
        raise RuntimeError(
            "There is no TaskList with slug specified for TODO_DEFAULT_LIST_SLUG in settings."
        )

    if request.POST:
        form = AddExternalTaskForm(request.POST)

        if form.is_valid():
            current_site = Site.objects.get_current()
            task = form.save(commit=False)
            task.task_list = TaskList.objects.get(slug=settings.TODO_DEFAULT_LIST_SLUG)
            task.created_by = request.user
            if defaults("TODO_DEFAULT_ASSIGNEE"):
                task.assigned_to = get_user_model().objects.get(username=settings.TODO_DEFAULT_ASSIGNEE)
            task.save()

            # Send email to assignee if we have one
            if task.assigned_to:
                email_subject = render_to_string(
                    "todo/email/assigned_subject.txt", {"task": task.title}
                )
                email_body = render_to_string(
                    "todo/email/assigned_body.txt", {"task": task, "site": current_site}
                )
                try:
                    send_mail(
                        email_subject,
                        email_body,
                        task.created_by.email,
                        [task.assigned_to.email],
                        fail_silently=False,
                    )
                except ConnectionRefusedError:
                    messages.warning(
                        request, "Task saved but mail not sent. Contact your administrator."
                    )

            messages.success(
                request, "Your trouble ticket has been submitted. We'll get back to you soon."
            )
            return redirect(defaults("TODO_PUBLIC_SUBMIT_REDIRECT"))

    else:
        form = AddExternalTaskForm(initial={"priority": 999})

    context = {"form": form}

    return render(request, "todo/add_task_external.html", context)

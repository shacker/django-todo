import datetime
import os

import bleach
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from todo.features import HAS_TASK_MERGE
from todo.forms import AddEditTaskForm
from todo.models import Attachment, Comment, Task
from todo.utils import (
    send_email_to_thread_participants,
    staff_check,
    toggle_task_completed,
    user_can_read_task,
)

if HAS_TASK_MERGE:
    from dal import autocomplete


def handle_add_comment(request, task):
    if not request.POST.get("add_comment"):
        return

    Comment.objects.create(
        author=request.user, task=task, body=bleach.clean(request.POST["comment-body"], strip=True)
    )

    send_email_to_thread_participants(
        task,
        request.POST["comment-body"],
        request.user,
        subject='New comment posted on task "{}"'.format(task.title),
    )

    messages.success(request, "Comment posted. Notification email sent to thread participants.")


@login_required
@user_passes_test(staff_check)
def task_detail(request, task_id: int) -> HttpResponse:
    """View task details. Allow task details to be edited. Process new comments on task.
    """

    task = get_object_or_404(Task, pk=task_id)
    comment_list = Comment.objects.filter(task=task_id).order_by("-date")

    # Ensure user has permission to view task. Admins can view all tasks.
    # Get the group this task belongs to, and check whether current user is a member of that group.
    if not user_can_read_task(task, request.user):
        raise PermissionDenied

    # Handle task merging
    if not HAS_TASK_MERGE:
        merge_form = None
    else:

        class MergeForm(forms.Form):
            merge_target = forms.ModelChoiceField(
                queryset=Task.objects.all(),
                widget=autocomplete.ModelSelect2(
                    url=reverse("todo:task_autocomplete", kwargs={"task_id": task_id})
                ),
            )

        # Handle task merging
        if not request.POST.get("merge_task_into"):
            merge_form = MergeForm()
        else:
            merge_form = MergeForm(request.POST)
            if merge_form.is_valid():
                merge_target = merge_form.cleaned_data["merge_target"]
            if not user_can_read_task(merge_target, request.user):
                raise PermissionDenied

            task.merge_into(merge_target)
            return redirect(reverse("todo:task_detail", kwargs={"task_id": merge_target.pk}))

    # Save submitted comments
    handle_add_comment(request, task)

    # Save task edits
    if not request.POST.get("add_edit_task"):
        form = AddEditTaskForm(request.user, instance=task, initial={"task_list": task.task_list})
    else:
        form = AddEditTaskForm(
            request.user, request.POST, instance=task, initial={"task_list": task.task_list}
        )

        if form.is_valid():
            item = form.save(commit=False)
            item.note = bleach.clean(form.cleaned_data["note"], strip=True)
            item.save()
            messages.success(request, "The task has been edited.")
            return redirect(
                "todo:list_detail", list_id=task.task_list.id, list_slug=task.task_list.slug
            )

    # Mark complete
    if request.POST.get("toggle_done"):
        results_changed = toggle_task_completed(task.id)
        if results_changed:
            messages.success(request, f"Changed completion status for task {task.id}")

        return redirect("todo:task_detail", task_id=task.id)

    if task.due_date:
        thedate = task.due_date
    else:
        thedate = datetime.datetime.now()

    # Handle uploaded files
    if request.FILES.get("attachment_file_input"):
        file = request.FILES.get("attachment_file_input")

        # Validate inbound file extension against allowed filetypes
        # FIXME: Move defaults to centralized module
        allowed_extensions = (
            settings.TODO_ALLOWED_FILE_ATTACHMENTS
            if hasattr(settings, "TODO_ALLOWED_FILE_ATTACHMENTS")
            else [".jpg", ".gif", ".csv", ".pdf", ".zip"]
        )
        name, extension = os.path.splitext(file.name)
        if extension not in allowed_extensions:
            messages.error(request, f"This site does not allow upload of {extension} files.")
            return redirect("todo:task_detail", task_id=task.id)

        Attachment.objects.create(
            task=task, added_by=request.user, timestamp=datetime.datetime.now(), file=file
        )
        return redirect("todo:task_detail", task_id=task.id)

    # Settings for file attachments defaults to True
    # FIXME: Move settings defaults to a central location?
    attachments_enabled = True
    if (
        hasattr(settings, "TODO_ALLOW_FILE_ATTACHMENTS")
        and not settings.TODO_ALLOW_FILE_ATTACHMENTS
    ):
        attachments_enabled = False

    context = {
        "task": task,
        "comment_list": comment_list,
        "form": form,
        "merge_form": merge_form,
        "thedate": thedate,
        "comment_classes": getattr(settings, "TODO_COMMENT_CLASSES", []),
        "attachments_enabled": attachments_enabled,
    }

    return render(request, "todo/task_detail.html", context)

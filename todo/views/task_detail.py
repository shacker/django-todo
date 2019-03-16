import bleach
import datetime

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator

from todo.forms import AddEditTaskForm
from todo.models import Comment, Task
from todo.utils import send_email_to_thread_participants, toggle_task_completed, staff_check, user_can_read_task
from todo.features import HAS_TASK_MERGE


if HAS_TASK_MERGE:
    from dal import autocomplete
    from todo.views.task_autocomplete import TaskAutocomplete


def handle_add_comment(request, task):
    if not request.POST.get("add_comment"):
        return

    Comment.objects.create(
        author=request.user,
        task=task,
        body=bleach.clean(request.POST["comment-body"], strip=True),
    )

    send_email_to_thread_participants(
        task,
        request.POST["comment-body"],
        request.user,
        subject='New comment posted on task "{}"'.format(task.title),
    )

    messages.success(
        request, "Comment posted. Notification email sent to thread participants."
    )


@login_required
@user_passes_test(staff_check)
def task_detail(request, task_id: int) -> HttpResponse:
    """View task details. Allow task details to be edited. Process new comments on task.
    """

    task = get_object_or_404(Task, pk=task_id)
    comment_list = Comment.objects.filter(task=task_id).order_by('-date')

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
            return redirect(reverse(
                "todo:task_detail",
                kwargs={"task_id": merge_target.pk}
            ))

    # Save submitted comments
    handle_add_comment(request, task)

    # Save task edits
    if not request.POST.get("add_edit_task"):
        form = AddEditTaskForm(
            request.user, instance=task, initial={"task_list": task.task_list}
        )
    else:
        form = AddEditTaskForm(
            request.user,
            request.POST,
            instance=task,
            initial={"task_list": task.task_list},
        )

        if form.is_valid():
            item = form.save(commit=False)
            item.note = bleach.clean(form.cleaned_data["note"], strip=True)
            item.save()
            messages.success(request, "The task has been edited.")
            return redirect(
                "todo:list_detail",
                list_id=task.task_list.id,
                list_slug=task.task_list.slug,
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

    context = {
        "task": task,
        "comment_list": comment_list,
        "form": form,
        "merge_form": merge_form,
        "thedate": thedate,
        "comment_classes": getattr(settings, 'TODO_COMMENT_CLASSES', []),
    }

    return render(request, "todo/task_detail.html", context)

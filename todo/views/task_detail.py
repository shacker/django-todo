import datetime

import bleach
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from todo.forms import AddEditTaskForm
from todo.models import Comment, Task
from todo.utils import send_email_to_thread_participants, toggle_task_completed, staff_check


@login_required
@user_passes_test(staff_check)
def task_detail(request, task_id: int) -> HttpResponse:
    """View task details. Allow task details to be edited. Process new comments on task.
    """

    task = get_object_or_404(Task, pk=task_id)
    comment_list = Comment.objects.filter(task=task_id)

    # Ensure user has permission to view task. Admins can view all tasks.
    # Get the group this task belongs to, and check whether current user is a member of that group.
    if task.task_list.group not in request.user.groups.all() and not request.user.is_staff:
        raise PermissionDenied

    # Save submitted comments
    if request.POST.get("add_comment"):
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
        messages.success(request, "Comment posted. Notification email sent to thread participants.")

    # Save task edits
    if request.POST.get("add_edit_task"):
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
    else:
        form = AddEditTaskForm(request.user, instance=task, initial={"task_list": task.task_list})

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

    context = {"task": task, "comment_list": comment_list, "form": form, "thedate": thedate}

    return render(request, "todo/task_detail.html", context)

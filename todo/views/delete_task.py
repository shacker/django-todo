from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from todo.models import Task

@login_required
def delete_task(request, task_id: int) -> HttpResponse:
    """Delete specified task.
    Redirect to the list from which the task came.
    """

    task = get_object_or_404(Task, pk=task_id)

    # Permissions
    if not (
        (task.created_by == request.user)
        or (task.assigned_to == request.user)
        or (task.task_list.group in request.user.groups.all())
    ):
        raise PermissionDenied

    tlist = task.task_list
    task.delete()

    messages.success(request, "Task '{}' has been deleted".format(task.title))
    return redirect(
        reverse("todo:list_detail", kwargs={"list_id": tlist.id, "list_slug": tlist.slug})
    )

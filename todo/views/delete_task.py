from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from todo.models import Task
from todo.utils import staff_check


@login_required
@user_passes_test(staff_check)
def delete_task(request, task_id: int) -> HttpResponse:
    """Delete specified task.
    Redirect to the list from which the task came.
    """

    if request.method == "POST":
        task = get_object_or_404(Task, pk=task_id)

        redir_url = reverse(
            "todo:list_detail",
            kwargs={"list_id": task.task_list.id, "list_slug": task.task_list.slug},
        )

        # Permissions
        if not (
            (task.created_by == request.user)
            or (request.user.is_superuser)
            or (task.assigned_to == request.user)
            or (task.task_list.group in request.user.groups.all())
        ):
            raise PermissionDenied

        task.delete()

        messages.success(request, "Task '{}' has been deleted".format(task.title))
        return redirect(redir_url)

    else:
        raise PermissionDenied

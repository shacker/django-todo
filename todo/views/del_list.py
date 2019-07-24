from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from todo.models import Task, TaskList
from todo.utils import staff_check


@login_required
@user_passes_test(staff_check)
def del_list(request, list_id: int, list_slug: str) -> HttpResponse:
    """Delete an entire list. Only staff members should be allowed to access this view.
    """
    task_list = get_object_or_404(TaskList, id=list_id)

    # Ensure user has permission to delete list. Get the group this list belongs to,
    # and check whether current user is a member of that group AND a staffer.
    if task_list.group not in request.user.groups.all():
        raise PermissionDenied    
    if not request.user.is_staff:
        raise PermissionDenied

    if request.method == "POST":
        TaskList.objects.get(id=task_list.id).delete()
        messages.success(request, "{list_name} is gone.".format(list_name=task_list.name))
        return redirect("todo:lists")
    else:
        task_count_done = Task.objects.filter(task_list=task_list.id, completed=True).count()
        task_count_undone = Task.objects.filter(task_list=task_list.id, completed=False).count()
        task_count_total = Task.objects.filter(task_list=task_list.id).count()

    context = {
        "task_list": task_list,
        "task_count_done": task_count_done,
        "task_count_undone": task_count_undone,
        "task_count_total": task_count_total,
    }

    return render(request, "todo/del_list.html", context)

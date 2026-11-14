from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from todo.models import Task
from todo.utils import staff_check


@csrf_exempt
@login_required
@user_passes_test(staff_check)
def reorder_tasks(request) -> HttpResponse:
    """Handle task re-ordering (priorities) from JQuery drag/drop in list_detail.html
    """
    newtasklist = request.POST.getlist("tasktable[]")
    if newtasklist:
        # First task in received list is always empty - remove it
        del newtasklist[0]

        # Re-prioritize each task in list
        i = 1
        for id in newtasklist:
            try:
                task = Task.objects.get(pk=id)
            except Task.DoesNotExist:
                # Can occur if task is deleted behind the scenes during re-ordering.
                # Not easy to remove it from the UI without page refresh, but prevent crash.
                continue

            # Only reorder tasks belonging to a list in one of the user's groups.
            # Without this check any logged-in user could change the priority of
            # tasks in other groups' lists by posting arbitrary task ids.
            if not (
                request.user.is_superuser
                or task.task_list.group in request.user.groups.all()
            ):
                continue

            task.priority = i
            task.save()
            i += 1

    # All views must return an httpresponse of some kind ... without this we get
    # error 500s in the log even though things look peachy in the browser.
    return HttpResponse(status=201)

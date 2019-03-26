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
                task.priority = i
                task.save()
                i += 1
            except Task.DoesNotExist:
                # Can occur if task is deleted behind the scenes during re-ordering.
                # Not easy to remove it from the UI without page refresh, but prevent crash.
                pass

    # All views must return an httpresponse of some kind ... without this we get
    # error 500s in the log even though things look peachy in the browser.
    return HttpResponse(status=201)

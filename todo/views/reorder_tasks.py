from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from todo.models import Task
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@login_required
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
            task = Task.objects.get(pk=id)
            task.priority = i
            task.save()
            i += 1

    # All views must return an httpresponse of some kind ... without this we get
    # error 500s in the log even though things look peachy in the browser.
    return HttpResponse(status=201)

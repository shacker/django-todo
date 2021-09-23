import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings

from todo.forms import SearchForm
from todo.models import Task, TaskList
from todo.utils import staff_check
from todo.defaults import defaults


@login_required
@user_passes_test(staff_check)
def list_lists(request) -> HttpResponse:
    """Homepage view - list of lists a user can view, and ability to add a list.
    """

    thedate = datetime.datetime.now()
    searchform = SearchForm(auto_id=False)
    user_groups = getattr(request.user, defaults("TODO_USER_GROUP_ATTRIBUTE"), "groups")

    # Make sure user belongs to at least one group.
    if not user_groups.all().exists():
        messages.warning(
            request,
            "You do not yet belong to any groups. Ask your administrator to add you to one.",
        )

    # Superusers see all lists
    lists = TaskList.objects.all().order_by("group__name", "name")
    if not request.user.is_superuser:
        lists = lists.filter(group__in=user_groups.all())

    list_count = lists.count()

    # superusers see all lists, so count shouldn't filter by just lists the admin belongs to
    if request.user.is_superuser:
        task_count = Task.objects.filter(completed=0).count()
    else:
        task_count = (
            Task.objects.filter(completed=0)
            .filter(task_list__group__in=user_groups.all())
            .count()
        )

    context = {
        "lists": lists,
        "thedate": thedate,
        "searchform": searchform,
        "list_count": list_count,
        "task_count": task_count,
    }

    return render(request, "todo/list_lists.html", context)

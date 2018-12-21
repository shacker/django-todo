from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.text import slugify

from todo.forms import AddTaskListForm
from todo.utils import staff_only


@staff_only
@login_required
def add_list(request) -> HttpResponse:
    """Allow users to add a new todo list to the group they're in.
    """

    if request.POST:
        form = AddTaskListForm(request.user, request.POST)
        if form.is_valid():
            try:
                newlist = form.save(commit=False)
                newlist.slug = slugify(newlist.name)
                newlist.save()
                messages.success(request, "A new list has been added.")
                return redirect("todo:lists")

            except IntegrityError:
                messages.warning(
                    request,
                    "There was a problem saving the new list. "
                    "Most likely a list with the same name in the same group already exists.",
                )
    else:
        if request.user.groups.all().count() == 1:
            form = AddTaskListForm(request.user, initial={"group": request.user.groups.all()[0]})
        else:
            form = AddTaskListForm(request.user)

    context = {"form": form}

    return render(request, "todo/add_list.html", context)

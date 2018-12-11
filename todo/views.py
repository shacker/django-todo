import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt

from todo.forms import AddTaskListForm, AddEditTaskForm, AddExternalTaskForm, SearchForm
from todo.models import Task, TaskList, Comment
from todo.utils import (
    send_notify_mail,
    send_email_to_thread_participants,
    )


def staff_only(function):
    """
    Custom view decorator allows us to raise 403 on insufficient permissions,
    rather than redirect user to login view.
    """
    def wrap(request, *args, **kwargs):
        if request.user.is_staff:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


@login_required
def list_lists(request) -> HttpResponse:
    """Homepage view - list of lists a user can view, and ability to add a list.
    """

    thedate = datetime.datetime.now()
    searchform = SearchForm(auto_id=False)

    # Make sure user belongs to at least one group.
    if request.user.groups.all().count() == 0:
        messages.warning(request, "You do not yet belong to any groups. Ask your administrator to add you to one.")

    # Superusers see all lists
    if request.user.is_superuser:
        lists = TaskList.objects.all().order_by('group', 'name')
    else:
        lists = TaskList.objects.filter(group__in=request.user.groups.all()).order_by('group', 'name')

    list_count = lists.count()

    # superusers see all lists, so count shouldn't filter by just lists the admin belongs to
    if request.user.is_superuser:
        task_count = Task.objects.filter(completed=0).count()
    else:
        task_count = Task.objects.filter(completed=0).filter(task_list__group__in=request.user.groups.all()).count()

    context = {
       "lists": lists,
       "thedate": thedate,
       "searchform": searchform,
       "list_count": list_count,
       "task_count": task_count,
    }

    return render(request, 'todo/list_lists.html', context)


@staff_only
@login_required
def del_list(request, list_id: int, list_slug: str) -> HttpResponse:
    """Delete an entire list. Danger Will Robinson! Only staff members should be allowed to access this view.
    """
    task_list = get_object_or_404(TaskList, id=list_id)

    # Ensure user has permission to delete list. Admins can delete all lists.
    # Get the group this list belongs to, and check whether current user is a member of that group.
    # FIXME: This means any group member can delete lists, which is probably too permissive.
    if task_list.group not in request.user.groups.all() and not request.user.is_staff:
        raise PermissionDenied

    if request.method == 'POST':
        TaskList.objects.get(id=task_list.id).delete()
        messages.success(request, "{list_name} is gone.".format(list_name=task_list.name))
        return redirect('todo:lists')
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

    return render(request, 'todo/del_list.html', context)


@login_required
def list_detail(request, list_id=None, list_slug=None, view_completed=False):
    """Display and manage tasks in a todo list.
    """

    # Defaults
    task_list = None
    form = None

    # Which tasks to show on this list view?
    if list_slug == "mine":
        tasks = Task.objects.filter(assigned_to=request.user)

    else:
        # Show a specific list, ensuring permissions.
        task_list = get_object_or_404(TaskList, id=list_id)
        if task_list.group not in request.user.groups.all() and not request.user.is_staff:
            raise PermissionDenied
        tasks = Task.objects.filter(task_list=task_list.id)

    # Additional filtering
    if view_completed:
        tasks = tasks.filter(completed=True)
    else:
        tasks = tasks.filter(completed=False)

    # ######################
    #  Add New Task Form
    # ######################

    if request.POST.getlist('add_edit_task'):
        form = AddEditTaskForm(request.user, request.POST, initial={
            'assigned_to': request.user.id,
            'priority': 999,
            'task_list': task_list
        })

        if form.is_valid():
            new_task = form.save(commit=False)
            new_task.created_date = timezone.now()
            form.save()

            # Send email alert only if Notify checkbox is checked AND assignee is not same as the submitter
            if "notify" in request.POST and new_task.assigned_to and new_task.assigned_to != request.user:
                send_notify_mail(new_task)

            messages.success(request, "New task \"{t}\" has been added.".format(t=new_task.title))
            return redirect(request.path)
    else:
        # Don't allow adding new tasks on some views
        if list_slug not in ["mine", "recent-add", "recent-complete", ]:
            form = AddEditTaskForm(request.user, initial={
                'assigned_to': request.user.id,
                'priority': 999,
                'task_list': task_list,
            })

    context = {
        "list_id": list_id,
        "list_slug": list_slug,
        "task_list": task_list,
        "form": form,
        "tasks": tasks,
        "view_completed": view_completed,
    }

    return render(request, 'todo/list_detail.html', context)


@login_required
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
    if request.POST.get('add_comment'):
        Comment.objects.create(
            author=request.user,
            task=task,
            body=request.POST['comment-body'],
        )

        send_email_to_thread_participants(
            task, request.POST['comment-body'], request.user,
            subject='New comment posted on task "{}"'.format(task.title))
        messages.success(request, "Comment posted. Notification email sent to thread participants.")

    # Save task edits
    if request.POST.get('add_edit_task'):
        form = AddEditTaskForm(request.user, request.POST, instance=task, initial={'task_list': task.task_list})

        if form.is_valid():
            form.save()
            messages.success(request, "The task has been edited.")
            return redirect('todo:list_detail', list_id=task.task_list.id, list_slug=task.task_list.slug)
    else:
        form = AddEditTaskForm(request.user, instance=task, initial={'task_list': task.task_list})

    # Mark complete
    if request.POST.get('toggle_done'):
        results_changed = toggle_done([task.id, ])
        for res in results_changed:
            messages.success(request, res)

        return redirect('todo:task_detail', task_id=task.id,)

    if task.due_date:
        thedate = task.due_date
    else:
        thedate = datetime.datetime.now()

    context = {
        "task": task,
        "comment_list": comment_list,
        "form": form,
        "thedate": thedate,
    }

    return render(request, 'todo/task_detail.html', context)


@csrf_exempt
@login_required
def reorder_tasks(request) -> HttpResponse:
    """Handle task re-ordering (priorities) from JQuery drag/drop in list_detail.html
    """
    newtasklist = request.POST.getlist('tasktable[]')
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
                return redirect('todo:lists')

            except IntegrityError:
                messages.warning(
                    request,
                    "There was a problem saving the new list. "
                    "Most likely a list with the same name in the same group already exists.")
    else:
        if request.user.groups.all().count() == 1:
            form = AddTaskListForm(request.user, initial={"group": request.user.groups.all()[0]})
        else:
            form = AddTaskListForm(request.user)

    context = {
        "form": form,
    }

    return render(request, 'todo/add_list.html', context)


@login_required
def search(request) -> HttpResponse:
    """Search for tasks user has permission to see.
    """
    if request.GET:

        query_string = ''
        found_tasks = None
        if ('q' in request.GET) and request.GET['q'].strip():
            query_string = request.GET['q']

            found_tasks = Task.objects.filter(
                Q(title__icontains=query_string) |
                Q(note__icontains=query_string)
            )
        else:
            # What if they selected the "completed" toggle but didn't enter a query string?
            # We still need found_tasks in a queryset so it can be "excluded" below.
            found_tasks = Task.objects.all()

        if 'inc_complete' in request.GET:
            found_tasks = found_tasks.exclude(completed=True)

    else:
        query_string = None
        found_tasks =None

    # Only include tasks that are in groups of which this user is a member:
    if not request.user.is_superuser:
        found_tasks = found_tasks.filter(task_list__group__in=request.user.groups.all())

    context = {
        'query_string': query_string,
        'found_tasks': found_tasks
    }
    return render(request, 'todo/search_results.html', context)


@login_required
def external_add(request) -> HttpResponse:
    """Allow authenticated users who don't have access to the rest of the ticket system to file a ticket
    in the list specified in settings (e.g. django-todo can be used a ticket filing system for a school, where
    students can file tickets without access to the rest of the todo system).

    Publicly filed tickets are unassigned unless settings.DEFAULT_ASSIGNEE exists.
    """

    if not settings.TODO_DEFAULT_LIST_SLUG:
        raise RuntimeError("This feature requires TODO_DEFAULT_LIST_SLUG: in settings. See documentation.")

    if not TaskList.objects.filter(slug=settings.TODO_DEFAULT_LIST_SLUG).exists():
        raise RuntimeError("There is no TaskList with slug specified for TODO_DEFAULT_LIST_SLUG in settings.")

    if request.POST:
        form = AddExternalTaskForm(request.POST)

        if form.is_valid():
            current_site = Site.objects.get_current()
            task = form.save(commit=False)
            task.task_list = TaskList.objects.get(slug=settings.TODO_DEFAULT_LIST_SLUG)
            task.created_by = request.user
            if settings.TODO_DEFAULT_ASSIGNEE:
                task.assigned_to = User.objects.get(username=settings.TODO_DEFAULT_ASSIGNEE)
            task.save()

            # Send email to assignee if we have one
            if task.assigned_to:
                email_subject = render_to_string("todo/email/assigned_subject.txt", {'task': task.title})
                email_body = render_to_string("todo/email/assigned_body.txt", {'task': task, 'site': current_site, })
                try:
                    send_mail(
                        email_subject, email_body, task.created_by.email,
                        [task.assigned_to.email, ], fail_silently=False)
                except ConnectionRefusedError:
                    messages.warning(request, "Task saved but mail not sent. Contact your administrator.")

            messages.success(request, "Your trouble ticket has been submitted. We'll get back to you soon.")
            return redirect(settings.TODO_PUBLIC_SUBMIT_REDIRECT)

    else:
        form = AddExternalTaskForm(initial={'priority': 999})

    context = {
        "form": form,
    }

    return render(request, 'todo/add_task_external.html', context)


@login_required
def toggle_done(request, task_id: int) -> HttpResponse:
    """Toggle the completed status of a task from done to undone, or vice versa.
    Redirect to the list from which the task came.
    """

    task = get_object_or_404(Task, pk=task_id)

    # Permissions
    if not (
        (task.created_by == request.user) or
        (task.assigned_to == request.user) or
        (task.task_list.group in request.user.groups.all())
    ):
        raise PermissionDenied

    tlist = task.task_list
    task.completed = not task.completed
    task.save()

    messages.success(request, "Task status changed for '{}'".format(task.title))
    return redirect(reverse('todo:list_detail', kwargs={"list_id": tlist.id, "list_slug": tlist.slug}))



@login_required
def delete_task(request, task_id: int) -> HttpResponse:
    """Delete specified task.
    Redirect to the list from which the task came.
    """

    task = get_object_or_404(Task, pk=task_id)

    # Permissions
    if not (
        (task.created_by == request.user) or
        (task.assigned_to == request.user) or
        (task.task_list.group in request.user.groups.all())
    ):
        raise PermissionDenied

    tlist = task.task_list
    task.delete()

    messages.success(request, "Task '{}' has been deleted".format(task.title))
    return redirect(reverse('todo:list_detail', kwargs={"list_id": tlist.id, "list_slug": tlist.slug}))

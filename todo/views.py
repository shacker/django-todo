import datetime

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from todo import settings
from todo.forms import AddTaskListForm, AddItemForm, EditItemForm, AddExternalItemForm, SearchForm
from todo.models import Item, TaskList, Comment
from todo.utils import toggle_done, toggle_deleted, send_notify_mail


def check_user_allowed(user):
    """
    Verifies user is logged in, and in staff if that setting is enabled.
    Per-object permission checks (e.g. to view a particular list) must be in the views that handle those objects.
    """

    if settings.STAFF_ONLY:
        return user.is_authenticated and user.is_staff
    else:
        return user.is_authenticated


@user_passes_test(check_user_allowed)
def list_lists(request):
    """Homepage view - list of lists a user can view, and ability to add a list.
    """

    thedate = datetime.datetime.now()
    searchform = SearchForm(auto_id=False)

    # Make sure user belongs to at least one group.
    if request.user.groups.all().count() == 0:
        messages.error(request, "You do not yet belong to any groups. Ask your administrator to add you to one.")

    # Superusers see all lists
    if request.user.is_superuser:
        list_list = TaskList.objects.all().order_by('group', 'name')
    else:
        list_list = TaskList.objects.filter(group__in=request.user.groups.all()).order_by('group', 'name')

    list_count = list_list.count()

    # superusers see all lists, so count shouldn't filter by just lists the admin belongs to
    if request.user.is_superuser:
        item_count = Item.objects.filter(completed=0).count()
    else:
        item_count = Item.objects.filter(completed=0).filter(task_list__group__in=request.user.groups.all()).count()

    return render(request, 'todo/list_lists.html', locals())


@user_passes_test(check_user_allowed)
def del_list(request, list_id, list_slug):
    """Delete an entire list. Danger Will Robinson! Only staff members should be allowed to access this view.
    """
    task_list = get_object_or_404(TaskList, slug=list_slug)

    # Ensure user has permission to delete list. Admins can delete all lists.
    # Get the group this list belongs to, and check whether current user is a member of that group.
    if task_list.group not in request.user.groups.all() or not request.user.is_staff:
        raise PermissionDenied

    if request.method == 'POST':
        TaskList.objects.get(id=task_list.id).delete()
        messages.success(request, "{list_name} is gone.".format(list_name=task_list.name))
        return redirect('todo:lists')
    else:
        item_count_done = Item.objects.filter(task_list=task_list.id, completed=True).count()
        item_count_undone = Item.objects.filter(task_list=task_list.id, completed=False).count()
        item_count_total = Item.objects.filter(task_list=task_list.id).count()

    return render(request, 'todo/del_list.html', locals())


def list_detail(request, list_id=None, list_slug=None, view_completed=False):
    """Display and manage items in a todo list.
    """

    if not list_slug == "mine":
        task_list = get_object_or_404(TaskList, id=list_id, slug=list_slug)

        # Ensure user has permission to view list. Admins can view all lists.
        # Get the group this task_list belongs to, and check whether current user is a member of that group.
        if task_list.group not in request.user.groups.all() and not request.user.is_staff:
            raise PermissionDenied

    if request.POST:
        # Process completed and deleted requests on each POST
        toggle_done(request, request.POST.getlist('toggle_done_tasks'))
        toggle_deleted(request, request.POST.getlist('toggle_deleted_tasks'))

    if list_slug == "mine":
        items = Item.objects.filter(assigned_to=request.user)
    else:
        task_list = get_object_or_404(TaskList, id=list_id)
        items = Item.objects.filter(task_list=task_list.id)

    # Apply filters to base queryset
    if view_completed:
        items = items.filter(completed=True)
    else:
        items = items.filter(completed=False)

    # ######################
    #  Add New Task Form
    # ######################

    if request.POST.getlist('add_task'):
        form = AddItemForm(task_list, request.POST, initial={
            'assigned_to': request.user.id,
            'priority': 999,
        })

        if form.is_valid():
            new_task = form.save()

            # Send email alert only if Notify checkbox is checked AND assignee is not same as the submitter
            if "notify" in request.POST and new_task.assigned_to != request.user:
                send_notify_mail(request, new_task)

            messages.success(request, "New task \"{t}\" has been added.".format(t=new_task.title))
            return redirect(request.path)
    else:
        # Don't allow adding new tasks on some views
        if list_slug != "mine" and list_slug != "recent-add" and list_slug != "recent-complete":
            form = AddItemForm(task_list=task_list, initial={
                'assigned_to': request.user.id,
                'priority': 999,
            })

    return render(request, 'todo/list_detail.html', locals())


@user_passes_test(check_user_allowed)
def task_detail(request, task_id):
    """View task details. Allow task details to be edited.
    """
    task = get_object_or_404(Item, pk=task_id)
    comment_list = Comment.objects.filter(task=task_id)

    # Ensure user has permission to view item. Admins can view all tasks.
    # Get the group this task belongs to, and check whether current user is a member of that group.
    if task.task_list.group not in request.user.groups.all() and not request.user.is_staff:
        raise PermissionDenied

    if request.POST:
        form = EditItemForm(request.POST, instance=task)

        if form.is_valid():
            form.save()

            # Also save submitted comment, if non-empty
            if request.POST['comment-body']:
                c = Comment(
                    author=request.user,
                    task=task,
                    body=request.POST['comment-body'],
                )
                c.save()

                # And email comment to all people who have participated in this thread.
                current_site = Site.objects.get_current()
                email_subject = render_to_string("todo/email/assigned_subject.txt", {'task': task})
                email_body = render_to_string(
                    "todo/email/newcomment_body.txt",
                    {'task': task, 'body': request.POST['comment-body'], 'site': current_site, 'user': request.user}
                )

                # Get list of all thread participants - everyone who has commented on it plus task creator.
                commenters = Comment.objects.filter(task=task)
                recip_list = [c.author.email for c in commenters]
                recip_list.append(task.created_by.email)
                recip_list = list(set(recip_list))  # Eliminate duplicates

                try:
                    send_mail(email_subject, email_body, task.created_by.email, recip_list, fail_silently=False)
                    messages.success(request, "Comment sent to thread participants.")
                except ConnectionRefusedError:
                    messages.error(request, "Comment saved but mail not sent. Contact your administrator.")

            messages.success(request, "The task has been edited.")

            return redirect('todo:list_detail', list_id=task.task_list.id, list_slug=task.task_list.slug)
    else:
        form = EditItemForm(instance=task)
        if task.due_date:
            thedate = task.due_date
        else:
            thedate = datetime.datetime.now()

    return render(request, 'todo/task_detail.html', locals())


@csrf_exempt
@user_passes_test(check_user_allowed)
def reorder_tasks(request):
    """Handle task re-ordering (priorities) from JQuery drag/drop in list_detail.html
    """
    newtasklist = request.POST.getlist('tasktable[]')
    # First item in received list is always empty - remove it
    del newtasklist[0]

    # Re-prioritize each item in list
    i = 1
    for t in newtasklist:
        newitem = Item.objects.get(pk=t)
        newitem.priority = i
        newitem.save()
        i += 1

    # All views must return an httpresponse of some kind ... without this we get
    # error 500s in the log even though things look peachy in the browser.
    return HttpResponse(status=201)


@login_required
def external_add(request):
    """Allow users who don't have access to the rest of the ticket system to file a ticket in a specific list.
    Public tickets are unassigned unless settings.DEFAULT_ASSIGNEE exists.
    """
    if request.POST:
        form = AddExternalItemForm(request.POST)

        if form.is_valid():
            current_site = Site.objects.get_current()
            item = form.save(commit=False)
            item.list_id = settings.DEFAULT_LIST_ID
            item.created_by = request.user
            if settings.DEFAULT_ASSIGNEE:
                item.assigned_to = User.objects.get(username=settings.DEFAULT_ASSIGNEE)
            item.save()

            email_subject = render_to_string("todo/email/assigned_subject.txt", {'task': item.title})
            email_body = render_to_string("todo/email/assigned_body.txt", {'task': item, 'site': current_site, })
            try:
                send_mail(
                    email_subject, email_body, item.created_by.email, [item.assigned_to.email, ], fail_silently=False)
            except ConnectionRefusedError:
                messages.error(request, "Task saved but mail not sent. Contact your administrator.")

            messages.success(request, "Your trouble ticket has been submitted. We'll get back to you soon.")

            return redirect(settings.PUBLIC_SUBMIT_REDIRECT)

    else:
        form = AddExternalItemForm()

    return render(request, 'todo/add_task_external.html', locals())


@user_passes_test(check_user_allowed)
def add_list(request):
    """Allow users to add a new todo list to the group they're in.
    """
    if request.POST:
        form = AddTaskListForm(request.user, request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "A new list has been added.")
                return redirect('todo:lists')

            except IntegrityError:
                messages.error(
                    request,
                    "There was a problem saving the new list. "
                    "Most likely a list with the same name in the same group already exists.")
    else:
        if request.user.groups.all().count() == 1:
            form = AddTaskListForm(request.user, initial={"group": request.user.groups.all()[0]})
        else:
            form = AddTaskListForm(request.user)

    return render(request, 'todo/add_list.html', locals())


@user_passes_test(check_user_allowed)
def search_post(request):
    """Redirect POST'd search param to query GET string
    """
    if request.POST:
        q = request.POST.get('q')
        url = reverse('todo:search') + "?q=" + q
        return redirect(url)


@user_passes_test(check_user_allowed)
def search(request):
    """Search for tasks
    """
    if request.GET:

        query_string = ''
        found_items = None
        if ('q' in request.GET) and request.GET['q'].strip():
            query_string = request.GET['q']

            found_items = Item.objects.filter(
                Q(title__icontains=query_string) |
                Q(note__icontains=query_string)
            )
        else:

            # What if they selected the "completed" toggle but didn't type in a query string?
            # We still need found_items in a queryset so it can be "excluded" below.
            found_items = Item.objects.all()

        if 'inc_complete' in request.GET:
            found_items = found_items.exclude(completed=True)

    else:
        query_string = None
        found_items = None

    context = {
        'query_string': query_string,
        'found_items': found_items
    }
    return render(request, 'todo/search_results.html', context)

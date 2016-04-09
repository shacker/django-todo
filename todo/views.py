import datetime

from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

from todo import settings
from todo.forms import AddListForm, AddItemForm, EditItemForm, AddExternalItemForm, SearchForm
from todo.models import Item, List, Comment

# Need for links in email templates
current_site = Site.objects.get_current()


def check_user_allowed(user):
    """
    test for user_passes_test decorator
    """
    if settings.STAFF_ONLY:
        return user.is_authenticated() and user.is_staff
    else:
        return user.is_authenticated()


@user_passes_test(check_user_allowed)
def list_lists(request):
    """
    Homepage view - list of lists a user can view, and ability to add a list.
    """
    thedate = datetime.datetime.now()
    searchform = SearchForm(auto_id=False)

    # Make sure user belongs to at least one group.
    group_count = request.user.groups.all().count()
    if group_count == 0:
        messages.error(request, "You do not yet belong to any groups. Ask your administrator to add you to one.")

    # Superusers see all lists
    if request.user.is_superuser:
        list_list = List.objects.all().order_by('group', 'name')
    else:
        list_list = List.objects.filter(group__in=request.user.groups.all()).order_by('group', 'name')

    list_count = list_list.count()

    # superusers see all lists, so count shouldn't filter by just lists the admin belongs to
    if request.user.is_superuser:
        item_count = Item.objects.filter(completed=0).count()
    else:
        item_count = Item.objects.filter(completed=0).filter(list__group__in=request.user.groups.all()).count()

    return render(request, 'todo/list_lists.html', locals())


@user_passes_test(check_user_allowed)
def del_list(request, list_id, list_slug):
    """
    Delete an entire list. Danger Will Robinson! Only staff members should be allowed to access this view.
    """
    list = get_object_or_404(List, slug=list_slug)

    if request.method == 'POST':
        del_list = List.objects.get(id=list.id)
        messages.success(request, "{list_name} is gone.".format(list_name=del_list.name))
        del_list.delete()  # Delete after creating message, or message fails.
        return HttpResponseRedirect(reverse('todo-lists'))
    else:
        item_count_done = Item.objects.filter(list=list.id, completed=1).count()
        item_count_undone = Item.objects.filter(list=list.id, completed=0).count()
        item_count_total = Item.objects.filter(list=list.id).count()

    return render(request, 'todo/del_list.html', locals())


@user_passes_test(check_user_allowed)
def view_list(request, list_id=0, list_slug=None, view_completed=False):
    """
    Display and manage items in a list.
    """

    # Make sure the accessing user has permission to view this list.
    # Always authorize the "mine" view. Admins can view/edit all lists.
    if list_slug == "mine" or list_slug == "recent-add" or list_slug == "recent-complete":
        auth_ok = 1
    else:
        list = get_object_or_404(List, slug=list_slug)
        listid = list.id

        if list.group in request.user.groups.all() or request.user.is_staff or list_slug == "mine":
            auth_ok = True  # User is authorized for this view
        else:  # User does not belong to the group this list is attached to
            messages.error(request, "You do not have permission to view/edit this list.")

    # Check for items in the mark_done POST array. If present, change status to complete.
    if request.POST.getlist('mark_done'):
        done_items = request.POST.getlist('mark_done')
        for item in done_items:
            i = Item.objects.get(id=item)
            i.completed = 1
            i.completed_date = datetime.datetime.now()
            i.save()
            messages.success(request, "Item \"{i}\" marked complete.".format(i=i.title))

    # Undo: Set completed items back to incomplete
    if request.POST.getlist('undo_completed_task'):
        undone_items = request.POST.getlist('undo_completed_task')
        for item in undone_items:
            i = Item.objects.get(id=item)
            i.completed = False
            i.save()
            messages.success(request, "Previously completed task \"{i}\" marked incomplete.".format(i=i.title))

    # And delete any requested items
    if request.POST.getlist('del_task'):
        deleted_items = request.POST.getlist('del_task')
        for item in deleted_items:
            i = Item.objects.get(id=item)
            i.delete()
            messages.success(request, "Item \"{i}\" deleted.".format(i=i.title))

    # Delete any already-completed items
    if request.POST.getlist('del_completed_task'):
        deleted_items = request.POST.getlist('del_completed_task')
        for item in deleted_items:
            i = Item.objects.get(id=item)
            i.delete()
            messages.success(request, "Deleted previously completed item \"{i}\".".format(i=i.title))

    thedate = datetime.datetime.now()
    created_date = "%s-%s-%s" % (thedate.year, thedate.month, thedate.day)

    # Get list of items with this list ID, or filter on items assigned to me, or recently added/completed
    if list_slug == "mine":
        task_list = Item.objects.filter(assigned_to=request.user, completed=False)
        completed_list = Item.objects.filter(assigned_to=request.user, completed=True)

    elif list_slug == "recent-add":
        # Only show items in lists that are in groups that the current user is also in.
        # Assume this only includes uncompleted items to avoid confusion.
        task_list = Item.objects.filter(
            list__group__in=(request.user.groups.all()),
            completed=False).order_by('-created_date')[:50]

    elif list_slug == "recent-complete":
        # Only show items in lists that are in groups that the current user is also in.
        task_list = Item.objects.filter(
            list__group__in=request.user.groups.all(),
            completed=True).order_by('-completed_date')[:50]

    else:
        task_list = Item.objects.filter(list=list.id, completed=0)
        completed_list = Item.objects.filter(list=list.id, completed=1)

    if request.POST.getlist('add_task'):
        form = AddItemForm(list, request.POST, initial={
            'assigned_to': request.user.id,
            'priority': 999,
        })

        if form.is_valid():
            new_task = form.save()

            # Send email alert only if Notify checkbox is checked AND assignee is not same as the submitter
            if "notify" in request.POST:
                if new_task.assigned_to != request.user:

                    # Send email
                    email_subject = render_to_string("todo/email/assigned_subject.txt", {'task': new_task})
                    email_body = render_to_string(
                        "todo/email/assigned_body.txt",
                        {'task': new_task, 'site': current_site, })
                    try:
                        send_mail(
                            email_subject, email_body, new_task.created_by.email,
                            [new_task.assigned_to.email], fail_silently=False)
                    except:
                        messages.error(request, "Task saved but mail not sent. Contact your administrator.")

            messages.success(request, "New task \"{t}\" has been added.".format(t=new_task.title))

            return HttpResponseRedirect(request.path)
    else:
        # Don't allow adding new tasks on some views
        if list_slug != "mine" and list_slug != "recent-add" and list_slug != "recent-complete":
            form = AddItemForm(list, initial={
                'assigned_to': request.user.id,
                'priority': 999,
            })

    return render(request, 'todo/view_list.html', locals())


@user_passes_test(check_user_allowed)
def view_task(request, task_id):
    """
    View task details. Allow task details to be edited.
    """
    task = get_object_or_404(Item, pk=task_id)
    comment_list = Comment.objects.filter(task=task_id)

    # Ensure user has permission to view item.
    # Get the group this task belongs to, and check whether current user is a member of that group.
    # Admins can edit all tasks.

    if task.list.group in request.user.groups.all() or request.user.is_staff:
        auth_ok = True

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
                    email_subject = render_to_string("todo/email/assigned_subject.txt", {'task': task})
                    email_body = render_to_string(
                        "todo/email/newcomment_body.txt",
                        {'task': task, 'body': request.POST['comment-body'], 'site': current_site, 'user': request.user}
                    )

                    # Get list of all thread participants - task creator plus everyone who has commented on it.
                    recip_list = []
                    recip_list.append(task.created_by.email)
                    commenters = Comment.objects.filter(task=task)
                    for c in commenters:
                        recip_list.append(c.author.email)
                    recip_list = set(recip_list)  # Eliminate duplicates

                    try:
                        send_mail(email_subject, email_body, task.created_by.email, recip_list, fail_silently=False)
                        messages.success(request, "Comment sent to thread participants.")
                    except:
                        messages.error(request, "Comment saved but mail not sent. Contact your administrator.")

                messages.success(request, "The task has been edited.")

                return HttpResponseRedirect(reverse('todo-incomplete_tasks', args=[task.list.id, task.list.slug]))
        else:
            form = EditItemForm(instance=task)
            if task.due_date:
                thedate = task.due_date
            else:
                thedate = datetime.datetime.now()
    else:
        messages.info(request, "You do not have permission to view/edit this task.")

    return render(request, 'todo/view_task.html', locals())


@csrf_exempt
@user_passes_test(check_user_allowed)
def reorder_tasks(request):
    """
    Handle task re-ordering (priorities) from JQuery drag/drop in view_list.html
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
    """
    Allow users who don't have access to the rest of the ticket system to file a ticket in a specific list.
    This is useful if, for example, a core web team are in a group that can file todos for each other,
    but you also want students to be able to post trouble tickets to a list just for the sysadmin. This
    way we don't have to put all users into a group that gives them access to the whole ticket system.
    """
    if request.POST:
        form = AddExternalItemForm(request.POST)

        if form.is_valid():
            item = form.save(commit=False)
            item.list_id = settings.DEFAULT_LIST_ID
            item.created_by = request.user
            item.assigned_to = User.objects.get(username=settings.DEFAULT_ASSIGNEE)
            item.save()

            email_subject = render_to_string("todo/email/assigned_subject.txt", {'task': item.title})
            email_body = render_to_string("todo/email/assigned_body.txt", {'task': item, 'site': current_site, })
            try:
                send_mail(
                    email_subject, email_body, item.created_by.email, [item.assigned_to.email, ], fail_silently=False)
            except:
                messages.error(request, "Task saved but mail not sent. Contact your administrator.")

            messages.success(request, "Your trouble ticket has been submitted. We'll get back to you soon.")

            return HttpResponseRedirect(settings.PUBLIC_SUBMIT_REDIRECT)
    else:
        form = AddExternalItemForm()

    return render(request, 'todo/add_external_task.html', locals())


@user_passes_test(check_user_allowed)
def add_list(request):
    """
    Allow users to add a new todo list to the group they're in.
    """
    if request.POST:
        form = AddListForm(request.user, request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "A new list has been added.")
                return HttpResponseRedirect(request.path)
            except IntegrityError:
                messages.error(
                    request,
                    "There was a problem saving the new list. "
                    "Most likely a list with the same name in the same group already exists.")
    else:
        if request.user.groups.all().count() == 1:
            form = AddListForm(request.user, initial={"group": request.user.groups.all()[0]})
        else:
            form = AddListForm(request.user)

    return render(request, 'todo/add_list.html', locals())


@user_passes_test(check_user_allowed)
def search_post(request):
    """
    Redirect POST'd search param to query GET string
    """
    if request.POST:
        q = request.POST.get('q')
        url = reverse('todo-search') + "?q=" + q
        return HttpResponseRedirect(url)


@user_passes_test(check_user_allowed)
def search(request):
    """
    Search for tasks
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

    return render(request,
        'todo/search_results.html',
        {'query_string': query_string, 'found_items': found_items},
        context_instance=RequestContext(request))

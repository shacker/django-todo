# django-todo

django-todo is a pluggable, multi-user, multi-group task management and
assignment application for Django, designed to be dropped into an existing site as a reusable app. django-todo can be used as a personal to-do tracker, or a group task management system, or a ticketing system for organizations (or all of these at once!)

**The best way to learn how django-todo works is to visit the live demo site at [django-todo.org](http://django-todo.org)!**

## Features

* Drag and drop task prioritization
* Email task notification
* Search
* Comments on tasks
* Public-facing submission form for tickets
* Mobile-friendly (work in progress)
* Separate view for My Tasks (across lists)
* Batch-import tasks via CSV
* Batch-export tasks in CSV Format
* Multiple file attachments per task (see settings)
* Integrated mail tracking (unify a task list with an email box)


## Requirements

* Django 2.0+
* Python 3.6+
* jQuery (full version, not "slim", for drag/drop prioritization)
* Bootstrap (to work with provided templates, though you can override them)
* bleach (`pip install bleach`)
* django-autocomplete-light (optional, required for task merging)

## Overview

We assume that your organization has multiple groups of employees, each with multiple users (where actual users and groups map to Django Users and Groups). Users may belong to multiple groups, and each group can have multiple todo lists.

You must have at least one Group set up in Django admin, and that group must have at least one User as a member. This is true even if you're the sole user of django-todo.

Users can view and modify all to-do lists belonging to their group(s). Only users with `is_staff` can add or delete lists.

Identical list names can exist in different groups, but not in the same group.

Emails are generated to the assigned-to person when new tasks are created.

File attachments of a few types are allowed on tasks by default. See settings to disable or to limit filetypes. If you are concerned about file sizes, limit them in your web server configuration (not currently handled separately by django-todo).

Comment threads can be added to tasks. Each participant in a thread receives email when new comments are added.

django-todo is auth-only. You must set up a login system and at least one group before deploying.

All tasks are "created by" the current user and can optionally be "assigned to" a specific user. Unassigned tickets appear as belonging to "anyone" in the UI.

django-todo v2 makes use of features only available in Django 2.0. It will not work in previous versions. v2 is only tested against Python 3.x -- no guarantees if running it against older versions.

## Installation

django-todo is a Django app, not a project site. It needs a site to live in. You can either install it into an existing Django project site, or clone the django-todo [demo site (GTD)](https://github.com/shacker/gtd).

If using your own site, be sure you have jQuery and Bootstrap wired up and working.

django-todo views that require it will insert additional CSS/JavaScript into page heads, so your project's base templates must include:

```jinja
{% block extrahead %}{% endblock extrahead %}
{% block extra_js %}{% endblock extra_js %}
```

django-todo comes with its own `todo/base.html`, which extends your master `base.html`. All content lives inside of:

`{% block content %}{% endblock %}`

If you use some other name for your main content area, you'll need to override and alter the provided templates.

All views are login-required. Therefore, you must have a working user authentication system.

For email notifications to work, make sure your site/project is [set up to send email](https://docs.djangoproject.com/en/2.0/topics/email/).

Make sure you've installed the Django "sites" framework and have specified the default site in settings, e.g. `SITE_ID = 1`

Put django-todo/todo somewhere on your Python path, or install via pip:

    pip install django-todo


Add to your settings:

```
INSTALLED_APPS = (
    ...
    'todo',
)
```

Migrate in database tables:

`python manage.py migrate todo`

Add to your URL conf:

`path('todo/', include('todo.urls', namespace="todo")),`

Add links to your site's navigation system:

```
<a href="{% url 'todo:lists' %}">Todo Lists</a>
<a href="{% url 'todo:mine' %}">My Tasks</a>
```

django-todo makes use of the Django `messages` system. Make sure you have something like [this](https://docs.djangoproject.com/en/2.1/ref/contrib/messages/#displaying-messages) (link) in your `base.html`.

Log in and access `/todo`!

### Customizing Templates

The provided templates are fairly bare-bones, and are meant as starting points only. Unlike previous versions of django-todo, they now ship as Bootstrap examples, but feel free to override them - there is no hard dependency on Bootstrap. To override a template, create a `todo` folder in your project's `templates` dir, then copy the template you want to override from django-todo source and into that dir.

### Filing Public Tickets

If you wish to use the public ticket-filing system, first create the list into which those tickets should be filed, then add its slug to `TODO_DEFAULT_LIST_SLUG` in settings (more on settings below).

## Settings

Optional configuration params, which can be added to your project settings:

```python
# Restrict access to ALL todo lists/views to `is_staff` users.
# If False or unset, all users can see all views (but more granular permissions are still enforced
# within views, such as requiring staff for adding and deleting lists).
TODO_STAFF_ONLY = True

# If you use the "public" ticket filing option, to whom should these tickets be assigned?
# Must be a valid username in your system. If unset, unassigned tickets go to "Anyone."
TODO_DEFAULT_ASSIGNEE = 'johndoe'

# If you use the "public" ticket filing option, to which list should these tickets be saved?
# Defaults to first list found, which is probably not what you want!
TODO_DEFAULT_LIST_SLUG = 'tickets'

# If you use the "public" ticket filing option, to which *named URL* should the user be
# redirected after submitting? (since they can't see the rest of the ticket system).
# Defaults to "/"
TODO_PUBLIC_SUBMIT_REDIRECT = 'dashboard'

# Enable or disable file attachments on Tasks
# Optionally limit list of allowed filetypes
TODO_ALLOW_FILE_ATTACHMENTS = True
TODO_ALLOWED_FILE_ATTACHMENTS = [".jpg", ".gif", ".csv", ".pdf", ".zip"]
TODO_MAXIMUM_ATTACHMENT_SIZE = 5000000  # In bytes

# additionnal classes the comment body should hold
# adding "text-monospace" makes comment monospace
TODO_COMMENT_CLASSES = []

# The following two settings are relevant only if you want todo to track a support mailbox -
# see Mail Tracking below.
TODO_MAIL_BACKENDS
TODO_MAIL_TRACKERS
```

The current django-todo version number is available from the [todo package](https://github.com/shacker/django-todo/blob/master/todo/__init__.py):

    python -c "import todo; print(todo.__version__)"

## Importing Tasks via CSV

django-todo has the ability to batch-import ("upsert") tasks from a specifically formatted CSV spreadsheet. This ability is provided through both a management command and a web interface.

**Management Command**

`./manage.py import_csv -f /path/to/file.csv`

**Web Importer**

Link from your navigation to `{url "todo:import_csv"}`. Follow the resulting link for the CSV web upload view.


### CSV Formatting

Copy `todo/data/import_example.csv` to another location on your system and edit in a spreadsheet or directly.

**Do not edit the header row!**

The first four columns: `'Title', 'Group', 'Task List', 'Created By'` are required -- all others are optional and should work pretty much exactly like manual task entry via the web UI.

Note: Internally, Tasks are keyed to TaskLists, not to Groups (TaskLists are in Gruops). However, we request the Group in the CSV
because it's possible to have multiple TaskLists with the same name in different groups; i.e. we need it for namespacing and permissions.


### Import Rules

Because data entered via CSV is not going through the same view permissions enforced in the rest of django-todo, and to simplify data dependency logic, and to pre-empt disagreements between django-todo users, the importer will *not* create new users, groups, or task lists. All users, groups, and task lists referenced in your CSV must already exist, and group memberships must be correct.

Any validation error (e.g. unparse-able dates, incorrect group memberships) **will result in that row being skipped.**

A report of rows upserted and rows skipped (with line numbers and reasons) is provided at the end of the run.

### Upsert Logic

For each valid row, we need to decide whether to create a new task or update an existing one. django-todo matches on the unique combination of the four required columns. If we find a task that matches those, we *update* the rest of the columns. In other words, if you import a CSV once, then edit the Assigned To for a task and import it again, the original task will be updated with a new assignee (and same for the other columns).

Otherwise we create a new task.


## Mail Tracking

What if you could turn django-todo into a shared mailbox? Django-todo includes an optional feature that allows emails
sent to a dedicated mailbox to be pushed into todo as new tasks, and responses to be added as comments on those tasks.
This allows support teams to work with a fully unified email + bug tracking system to avoid confusion over who's seen or
responded to what.

To enable mail tracking, you need to:

 - Define an email backend for outgoing emails
 - Define an email backend for incoming emails
 - Start a worker, which will wait for new emails

In settings:

```python
from todo.mail.producers import imap_producer
from todo.mail.consumers import tracker_consumer
from todo.mail.delivery import smtp_backend, console_backend

# email notifications configuration
# each task list can get its own delivery method
TODO_MAIL_BACKENDS = {
    # mail-queue is the name of the task list, not the worker name
    "mail-queue": smtp_backend(
        host="smtp.example.com",
        port=465,
        use_ssl=True,
        username="test@example.com",
        password="foobar",
        # used as the From field when sending notifications.
        # a username might be prepended later on
        from_address="test@example.com",
        # additionnal headers
        headers={}
    ),
}

# incoming mail worker configuration
TODO_MAIL_TRACKERS = {
    # configuration for worker "test_tracker"
    "test_tracker": {
        "producer": imap_producer(
            host="imap.example.com",
            username="text@example.com",
            password="foobar",
            # process_all=False, # by default, only unseen emails are processed
            # preserve=False, # delete emails if False
            # nap_duration=1, # duration of the pause between polling rounds
            # input_folder="INBOX", # where to read emails from
        ),
        "consumer": tracker_consumer(
            group="Mail Queuers",
            task_list_slug="mail-queue",
            priority=1,
            task_title_format="[TEST_MAIL] {subject}",
        )
    }
}
```

A mail worker can be started with:

```sh
./manage.py mail_worker test_tracker
```

Some views and URLs were renamed in 2.0 for logical consistency. If this affects you, see source code and the demo GTD site for reference to the new URL names.

If you want to log mail events, make sure to properly configure django logging:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```


## Running Tests

django-todo uses pytest exclusively for testing. The best way to run the suite is to clone django-todo into its own directory, install pytest, then:

	pip install pytest pytest-django
	pip install --editable .
	pytest -x -v

## Version History

**2.4.10** It is now possible to use unicode characters (such as Chinese) as the only chars in a list title.

**2.4.9** Fixed: Editing a task should not change its completed/incomplete status

**2.4.8** Fix bug when setting default values for unspecified settings

**2.4.7** Support custom user model in external_add

**2.4.6** Use `defaults` hash for default settings, update perms and tests

**2.4.5** Re-enable "notify" feature during task edit

**2.4.4** Fix issues with setup.py / installation

**2.4.0** Implement optional file attachments on tasks

**2.3.2** Update setup.py metadata

**2.3.1** Improve error handling for badly formatted or non-existent CSV uploads.

**2.3.0** Implement mail tracking system. Added ability to batch-import tasks via CSV. Fixed task re-ordering if task deleted behind the scenes.

**2.2.2** Update dependencies

**2.2.1** Convert task delete and toggle_done views to POST only

**2.2.0** Re-instate enforcement of TODO_STAFF_ONLY setting

**2.1.1** Correct Python version requirement in documentation to Python 3.6

**2.1.1** Split up views into separate modules.

**2.1.0** December 2018: No longer allowing Javascript in task or comment bodies. Misc bug fixes.

**2.0.3** April 2018: Bump production status in setup.py

**2.0.2** April 2018: Improve notification email subjects and bodies

**2.0.1** April 2018: Refactored "toggle done" and "delete" actions from list view.

**2.0** April 2018: Major project refactor, with almost completely rewritten views, templates, and todo's first real test suite.

**1.6.2** Added support for unicode characters in list name/slugs.

**1.6.1** Minor bug fixes.

**1.6** Allow unassigned ("Anyone") tasks. Clean-up / modernize templates and views. Testing infrastructure in place.

**1.5** flake8 support, Item note no longer a required field, fix warnings for Django 1.8, Python 2/3-compatible unicode strings, simple search for tasks, get_absolute_url() for items.

**1.4** - Removed styling from default templates. Added excludes fields from Form definitions to prevent warnings. Removed deprecated 'cycle' tags from templates. Added settings for various elements for public ticket submissions.

**1.3** - Removed stray direct_to_template reference. Quoted all named URL references for Django 1.5 compatibility.

**1.2** - Added CSRF protection to all sample templates. Added integrated search function. Now showing the ratio of completed/total items for each
list. Better separation of media and templates. Cleaned up Item editing form (removed extraneous fields). Re-assigning tasks now properly limits
the list of assignees. Moved project to github.

**1.1** - Completion date was set properly when checking items off a list, but not when saving from an Item detail page. Added a save method on Item to
fix. Fixed documentation bug re: context_processors. Newly added comments are now emailed to everyone who has participated in a thread on a task.

**1.0.1** - When viewing a single task that you want to close, it's useful to be able to comment on and close a task at the same time. We were using
django-comments so these were different models in different views. Solution was to stop using django-comments and roll our own, then rewire the
view. Apologies if you were using a previous version - you may need to port over your comments to the new system.

**1.0.0** - Major upgrade to release version. Drag and drop task prioritization. E-mail notifications (now works more like a ticket system). More
attractive date picker. Bug fixes.

**0.9.5** - Fixed jquery bug when editing existing events - datepicker now shows correct date. Removed that damned Django pony from base template.

**0.9.4** - Replaced str with unicode in models. Fixed links back to lists in "My Tasks" view.

**0.9.3** - Missing link to the individual task editing view

**0.9.2** - Now fails gracefully when trying to add a 2nd list with the same name to the same group. - Due dates for tasks are now truly optional. -
Corrected datetime editing conflict when editing tasks - Max length of a task name has been raised from 60 to 140 chars. If upgrading, please
modify your database accordingly (field todo_item.name = maxlength 140). - Security: Users supplied with direct task URLs can no longer view/edit
tasks outside their group scope Same for list views - authorized views only. - Correct item and group counts on homepage (note - admin users see
ALL groups, not just the groups they "belong" to)

**0.9.1** - Removed context_processors.py - leftover turdlet

**0.9** - First release

## Todo 2.0 Upgrade Notes

django-todo 2.0 was rebuilt almost from the ground up, and included some radical changes, including model name changes. As a result, it is *not compatible* with data from django-todo 1.x. If you would like to upgrade an existing installation, try this:

*  Use `./manage.py dumpdata todo --indent 4 > todo.json` to export your old todo data
*  Edit the dump file, replacing the old model names `Item` and `List` with the new model names (`Task` and `TaskList`)
*  Delete your existing todo data
*  Uninstall the old todo app and reinstall
*  Migrate, then use `./manage.py loaddata todo.json` to import the edited data

### Why not provide migrations?

That was the plan, but unfortunately, `makemigrations` created new tables and dropped the old ones, making this a destructive update. Renaming models is unfortunately not something `makemigrations` can do, and I really didn't want to keep the badly named original models. Sorry!

### Datepicker

django-todo no longer references a jQuery datepicker, but defaults to native html5 browser datepicker (not supported by Safari, unforunately). Feel free to implement one of your choosing.

### URLs

Some views and URLs were renamed for logical consistency. If this affects you, see source code and the demo GTD site for reference to the new URL names.

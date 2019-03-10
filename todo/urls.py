from django.urls import path

from todo import views

app_name = 'todo'

urlpatterns = [

    path(
        '',
        views.list_lists,
        name="lists"),

    # View reorder_tasks is only called by JQuery for drag/drop task ordering.
    path(
        'reorder_tasks/',
        views.reorder_tasks,
        name="reorder_tasks"),

    # Allow users to post tasks from outside django-todo (e.g. for filing tickets - see docs)
    path(
        'ticket/add/',
        views.external_add,
        name="external_add"),

    # Three paths into `list_detail` view
    path(
        'mine/',
        views.list_detail,
        {'list_slug': 'mine'},
        name="mine"),

    path(
        '<int:list_id>/<str:list_slug>/completed/',
        views.list_detail,
        {'view_completed': True},
        name='list_detail_completed'),

    path(
        '<int:list_id>/<str:list_slug>/',
        views.list_detail,
        name='list_detail'),

    path(
        '<int:list_id>/<str:list_slug>/delete/',
        views.del_list,
        name="del_list"),

    path(
        'add_list/',
        views.add_list,
        name="add_list"),

    path(
        'task/<int:task_id>/',
        views.task_detail,
        name='task_detail'),

    path(
        'toggle_done/<int:task_id>/',
        views.toggle_done,
        name='task_toggle_done'),

    path(
        'delete/<int:task_id>/',
        views.delete_task,
        name='delete_task'),

    path(
        'search/',
        views.search,
        name="search"),

    path(
        'import_csv/',
        views.import_csv,
        name="import_csv"),
]

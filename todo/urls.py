from django.conf.urls import url
from todo import views

urlpatterns = [
    url(r'^$', views.list_lists, name="todo-lists"),
    url(r'^mine/$', views.view_list, {'list_slug': 'mine'}, name="todo-mine"),
    url(r'^(?P<list_id>\d{1,4})/(?P<list_slug>[\w-]+)/delete$', views.del_list, name="todo-del_list"),
    url(r'^task/(?P<task_id>\d{1,6})$', views.view_task, name='todo-task_detail'),
    url(r'^(?P<list_id>\d{1,4})/(?P<list_slug>[\w-]+)$', views.view_list, name='todo-incomplete_tasks'),
    url(r'^(?P<list_id>\d{1,4})/(?P<list_slug>[\w-]+)/completed$', views.view_list, {'view_completed': True},
        name='todo-completed_tasks'),
    url(r'^add_list/$', views.add_list, name="todo-add_list"),
    url(r'^search-post/$', views.search_post, name="todo-search-post"),
    url(r'^search/$', views.search, name="todo-search"),

    # View reorder_tasks is only called by JQuery for drag/drop task ordering
    url(r'^reorder_tasks/$', views.reorder_tasks, name="todo-reorder_tasks"),

    url(r'^ticket/add/$', views.external_add, name="todo-external-add"),
    url(r'^recent/added/$', views.view_list, {'list_slug': 'recent-add'}, name="todo-recently_added"),
    url(r'^recent/completed/$', views.view_list, {'list_slug': 'recent-complete'},
        name="todo-recently_completed"),
]

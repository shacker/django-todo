from django.conf.urls import *
from django.contrib.auth import views as auth_views

urlpatterns = patterns('',
    url(r'^mine/$', 'todo.views.view_list',{'list_slug':'mine'},name="todo-mine"),
    url(r'^(?P<list_id>\d{1,4})/(?P<list_slug>[\w-]+)/delete$', 'todo.views.del_list',name="todo-del_list"),
    url(r'^task/(?P<task_id>\d{1,6})$', 'todo.views.view_task', name='todo-task_detail'),
    url(r'^(?P<list_id>\d{1,4})/(?P<list_slug>[\w-]+)$', 'todo.views.view_list', name='todo-incomplete_tasks'),
    url(r'^(?P<list_id>\d{1,4})/(?P<list_slug>[\w-]+)/completed$', 'todo.views.view_list', {'view_completed':1},name='todo-completed_tasks'),    
    url(r'^add_list/$', 'todo.views.add_list',name="todo-add_list"),
    url(r'^search/$', 'todo.views.search',name="todo-search"),    
    url(r'^$', 'todo.views.list_lists',name="todo-lists"),
    
    # View reorder_tasks is only called by JQuery for drag/drop task ordering
    url(r'^reorder_tasks/$', 'todo.views.reorder_tasks',name="todo-reorder_tasks"),
    
    url(r'^ticket/add/$', 'todo.views.external_add',name="todo-external-add"),    
    url(r'^recent/added/$', 'todo.views.view_list',{'list_slug':'recent-add'},name="todo-recently_added"),
    url(r'^recent/completed/$', 'todo.views.view_list',{'list_slug':'recent-complete'},name="todo-recently_completed"),    
)


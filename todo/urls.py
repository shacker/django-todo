from django.urls import path

from todo import views

app_name = 'todo'

urlpatterns = [
    path('', views.list_lists, name="lists"),
    path('mine/', views.view_list, {'list_slug': 'mine'}, name="mine"),
    path('<int:list_id>/<str:list_slug>/delete$', views.del_list, name="del_list"),
    path('task/<int:task_id>', views.view_task, name='task_detail'),
    path('<int:list_id>/<str:list_slug>', views.view_list, name='incomplete_tasks'),
    path('<int:list_id>/<str:list_slug>/completed$', views.view_list, {'view_completed': True}, name='completed_tasks'),
    path('add_list/', views.add_list, name="add_list"),

    # FIXME need both of these?
    path('search-post/', views.search_post, name="search-post"),
    path('search/', views.search, name="search"),

    # View reorder_tasks is only called by JQuery for drag/drop task ordering
    path('reorder_tasks/', views.reorder_tasks, name="reorder_tasks"),

    path('ticket/add/', views.external_add, name="external-add"),
    path('recent/added/', views.view_list, {'list_slug': 'recent-add'}, name="recently_added"),
    path('recent/completed/', views.view_list, {'list_slug': 'recent-complete'}, name="recently_completed"),
]

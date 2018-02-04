from django.urls import path

from todo import views

app_name = 'todo'

urlpatterns = [
    path('', views.list_lists, name="lists"),

    # Three paths into `list_detail` view
    path('<int:list_id>/<str:list_slug>/', views.list_detail, name='list_detail'),
    path('mine/', views.list_detail, {'list_slug': 'mine'}, name="mine"),
    path('<int:list_id>/<str:list_slug>/completed/', views.list_detail, {'view_completed': True}, name='completed_tasks'),

    path('<int:list_id>/<str:list_slug>/delete/', views.del_list, name="del_list"),
    path('add_list/', views.add_list, name="add_list"),

    path('task/<int:task_id>/', views.task_detail, name='task_detail'),

    # FIXME need both of these?
    path('search-post/', views.search_post, name="search-post"),
    path('search/', views.search, name="search"),

    # View reorder_tasks is only called by JQuery for drag/drop task ordering
    path('reorder_tasks/', views.reorder_tasks, name="reorder_tasks"),

    path('ticket/add/', views.external_add, name="external-add"),
    path('recent/added/', views.list_detail, {'list_slug': 'recent-add'}, name="recently_added"),
    path('recent/completed/', views.list_detail, {'list_slug': 'recent-complete'}, name="recently_completed"),
]

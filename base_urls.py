from django.urls import include, path

"""
This urlconf exists so we can run tests without an actual Django project
(Django expects ROOT_URLCONF to exist.) This helps the tests remain isolated.
For your project, ignore this file and add

`path('lists/', include('todo.urls')),`

to your site's urlconf.
"""

urlpatterns = [path("lists/", include("todo.urls"))]

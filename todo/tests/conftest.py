import pytest

from django.contrib.auth.models import Group

from todo.models import Task, TaskList



@pytest.fixture
def todo_setup(django_user_model):
    # Two groups with different users, two sets of tasks.

    g1 = Group.objects.create(name="Workgroup One")
    u1 = django_user_model.objects.create_user(username="u1", password="password", email="u1@example.com")
    u1.groups.add(g1)
    tlist1 = TaskList.objects.create(group=g1, name="Zip", slug="zip")
    Task.objects.create(created_by=u1, title="Task 1", task_list=tlist1, priority=1)
    Task.objects.create(created_by=u1, title="Task 2", task_list=tlist1, priority=2, completed=True)
    Task.objects.create(created_by=u1, title="Task 3", task_list=tlist1, priority=3)

    g2 = Group.objects.create(name="Workgroup Two")
    u2 = django_user_model.objects.create_user(username="u2", password="password", email="u2@example.com")
    u2.groups.add(g2)
    tlist2 = TaskList.objects.create(group=g2, name="Zap", slug="zap")
    Task.objects.create(created_by=u2, title="Task 1", task_list=tlist2, priority=1)
    Task.objects.create(created_by=u2, title="Task 2", task_list=tlist2, priority=2, completed=True)
    Task.objects.create(created_by=u2, title="Task 3", task_list=tlist2, priority=3)

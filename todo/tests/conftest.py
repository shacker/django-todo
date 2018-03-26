import pytest

from django.contrib.auth.models import Group

from todo.models import Item, TaskList


@pytest.fixture
def todo_setup(django_user_model):
    g1 = Group.objects.create(name="Weavers")
    u1 = django_user_model.objects.create(username="you", password="password")
    u1.groups.add(g1)
    tlist = TaskList.objects.create(group=g1, name="Zip", slug="zip")

    Item.objects.create(created_by=u1, title="Task 1", task_list=tlist, priority=1)
    Item.objects.create(created_by=u1, title="Task 2", task_list=tlist, priority=2)
    Item.objects.create(created_by=u1, title="Task 3", task_list=tlist, priority=3)

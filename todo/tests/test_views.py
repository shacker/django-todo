import pytest

from django.contrib.auth import get_user_model
from django.urls import reverse

from todo.models import Item, TaskList

"""
First the "smoketests" - do they respond at all for a logged in admin user?
Next permissions tests - some views should respond for staffers only.
After that, view contents and behaviors.
"""

# ### SMOKETESTS ###

@pytest.mark.django_db
def test_todo_setup(todo_setup):
    assert Item.objects.all().count() == 6


def test_view_list_lists(todo_setup, admin_client):
    url = reverse('todo:lists')
    response = admin_client.get(url)
    assert response.status_code == 200


def test_view_reorder(todo_setup, admin_client):
    url = reverse('todo:reorder_tasks')
    response = admin_client.get(url)
    assert response.status_code == 201  # Special case return value expected


def test_view_external_add(todo_setup, admin_client, settings):
    default_list = TaskList.objects.first()
    settings.TODO_DEFAULT_LIST_ID = default_list.id
    assert settings.TODO_DEFAULT_LIST_ID == default_list.id
    url = reverse('todo:external_add')
    response = admin_client.get(url)
    assert response.status_code == 200


def test_view_mine(todo_setup, admin_client):
    url = reverse('todo:mine')
    response = admin_client.get(url)
    assert response.status_code == 200


def test_view_list_completed(todo_setup, admin_client):
    tlist = TaskList.objects.get(slug="zip")
    url = reverse('todo:list_detail_completed', kwargs={'list_id': tlist.id, 'list_slug': tlist.slug})
    response = admin_client.get(url)
    assert response.status_code == 200


def test_view_list(todo_setup, admin_client):
    tlist = TaskList.objects.get(slug="zip")
    url = reverse('todo:list_detail', kwargs={'list_id': tlist.id, 'list_slug': tlist.slug})
    response = admin_client.get(url)
    assert response.status_code == 200


def test_del_list(todo_setup, admin_client):
    tlist = TaskList.objects.get(slug="zip")
    url = reverse('todo:del_list', kwargs={'list_id': tlist.id, 'list_slug': tlist.slug})
    response = admin_client.get(url)
    assert response.status_code == 200


def test_view_add_list(todo_setup, admin_client):
    url = reverse('todo:add_list')
    response = admin_client.get(url)
    assert response.status_code == 200


def test_view_task_detail(todo_setup, admin_client):
    task = Item.objects.first()
    url = reverse('todo:task_detail', kwargs={'task_id': task.id})
    response = admin_client.get(url)
    assert response.status_code == 200


def test_view_search(todo_setup, admin_client):
    url = reverse('todo:search')
    response = admin_client.get(url)
    assert response.status_code == 200


# ### PERMISSIONS ###

"""
Some views are for staff users only.
We've already smoke-tested with Admin user - try these with normal user.
"""


def test_view_add_list_nonadmin(todo_setup, client):
    url = reverse('todo:add_list')
    client.login(username="you", password="password")
    response = client.get(url)
    assert response.status_code == 403


def test_view_del_list_nonadmin(todo_setup, client):
    tlist = TaskList.objects.get(slug="zip")
    url = reverse('todo:del_list', kwargs={'list_id': tlist.id, 'list_slug': tlist.slug})
    client.login(username="you", password="password")
    response = client.get(url)
    assert response.status_code == 403


def test_view_list_mine(todo_setup, client):
    """View a list in a group I belong to.
    """
    tlist = TaskList.objects.get(slug="zip")  # User u1 is in this group's list
    url = reverse('todo:list_detail', kwargs={'list_id': tlist.id, 'list_slug': tlist.slug})
    client.login(username="u1", password="password")
    response = client.get(url)
    assert response.status_code == 200


def test_view_list_not_mine(todo_setup, client):
    """View a list in a group I don't belong to.
    """
    tlist = TaskList.objects.get(slug="zip")  # User u1 is in this group, user u2 is not.
    url = reverse('todo:list_detail', kwargs={'list_id': tlist.id, 'list_slug': tlist.slug})
    client.login(username="u2", password="password")
    response = client.get(url)
    assert response.status_code == 403



# TODO
# View a task in a list in a group I do / don't belong to.
# Mark complete
# staff_only decorator

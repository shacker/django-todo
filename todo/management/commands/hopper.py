from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from todo.models import Task, TaskList
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = """Create random list and task data for a few fake users."""

    def handle(self, *args, **options):

        # Create users and groups, add different users to different groups. Staff user is in both groups.
        bw_group = Group.objects.create(name='Basket Weavers')
        sd_group = Group.objects.create(name='Scuba Divers')
        usernames = ['user1', 'user2', 'staff_user']
        
        for username in usernames:
            get_user_model().objects.create_user(username=username, password="todo")

            if username == 'user1':
                u1 = get_user_model().objects.get(username=username)
                u1.groups.add(bw_group)

            if username == 'user2':
                u2 = get_user_model().objects.get(username=username)
                u2.groups.add(sd_group)

            if username == 'staff_user':
                staffer = get_user_model().objects.get(username=username, is_staff=True,)
                staffer.groups.add(bw_group)
                staffer.groups.add(sd_group)



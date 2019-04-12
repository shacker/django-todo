import factory
from faker import Faker
from titlecase import titlecase
import random

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.utils.text import slugify

from todo.models import Task, TaskList


num_lists = 5


def gen_title(tc=True):
    # faker doesn't provide a way to generate headlines in Title Case, without periods, so make our own.
    # With arg `tc=True`, Title Cases The Generated Text
    fake = Faker()
    thestr = fake.text(max_nb_chars=32).rstrip(".")
    if tc:
        thestr = titlecase(thestr)

    return thestr


def gen_content():
    # faker provides paragraphs as a list; convert with linebreaks
    fake = Faker()
    grafs = fake.paragraphs()
    thestr = ""
    for g in grafs:
        thestr += "{}\n\n".format(g)
    return thestr


class Command(BaseCommand):
    help = """Create random list and task data for a few fake users."""

    def add_arguments(self, parser):
        parser.add_argument(
            "-d",
            "--delete",
            help="Wipe out existing content before generating new.",
            action="store_true",
        )

    def handle(self, *args, **options):

        if options.get("delete"):
            # Wipe out previous contents? Cascade deletes the Tasks from the TaskLists.
            TaskList.objects.all().delete()
            print("Content from previous run deleted.")
            print("Working...")

        fake = Faker()  # Use to create user's names

        # Create users and groups, add different users to different groups. Staff user is in both groups.
        sd_group, created = Group.objects.get_or_create(name="Scuba Divers")
        bw_group, created = Group.objects.get_or_create(name="Basket Weavers")

        # Put user1 and user2 in one group, user3 and user4 in another
        usernames = ["user1", "user2", "user3", "user4", "staffer"]
        for username in usernames:
            if get_user_model().objects.filter(username=username).exists():
                user = get_user_model().objects.get(username=username)
            else:
                user = get_user_model().objects.create_user(
                    username=username,
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    email="{}@example.com".format(username),
                    password="todo",
                )

            if username in ["user1", "user2"]:
                user.groups.add(bw_group)

            if username in ["user3", "user4"]:
                user.groups.add(sd_group)

            if username == "staffer":
                user.is_staff = True
                user.first_name = fake.first_name()
                user.last_name = fake.last_name()
                user.save()
                user.groups.add(bw_group)
                user.groups.add(sd_group)

        # Create lists with tasks, plus one with fixed name for externally added tasks
        TaskListFactory.create_batch(5, group=bw_group)
        TaskListFactory.create_batch(5, group=sd_group)
        TaskListFactory.create(name="Public Tickets", slug="tickets", group=bw_group)

        print(
            "For each of two groups, created fake tasks in each of {} fake lists.".format(num_lists)
        )


class TaskListFactory(factory.django.DjangoModelFactory):
    """Group not generated here - call with group as arg."""

    class Meta:
        model = TaskList

    name = factory.LazyAttribute(lambda o: gen_title(tc=True))
    slug = factory.LazyAttribute(lambda o: slugify(o.name))
    group = None  # Pass this in

    @factory.post_generation
    def add_tasks(self, build, extracted, **kwargs):
        num = random.randint(5, 25)
        TaskFactory.create_batch(num, task_list=self)


class TaskFactory(factory.django.DjangoModelFactory):
    """TaskList not generated here - call with TaskList as arg."""

    class Meta:
        model = Task

    title = factory.LazyAttribute(lambda o: gen_title(tc=False))
    task_list = None  # Pass this in
    note = factory.LazyAttribute(lambda o: gen_content())
    priority = factory.LazyAttribute(lambda o: random.randint(1, 100))
    completed = factory.Faker("boolean", chance_of_getting_true=30)
    created_by = factory.LazyAttribute(
        lambda o: get_user_model().objects.get(username="staffer")
    )  # Randomized in post
    created_date = factory.Faker("date_this_year")

    @factory.post_generation
    def add_details(self, build, extracted, **kwargs):

        fake = Faker()  # Use to create user's names
        taskgroup = self.task_list.group

        self.created_by = taskgroup.user_set.all().order_by("?").first()

        if self.completed:
            self.completed_date = fake.date_this_year()

        # 1/3 of generated tasks have a due_date
        if random.randint(1, 3) == 1:
            self.due_date = fake.date_this_year()

        # 1/3 of generated tasks are assigned to someone in this tasks's group
        if random.randint(1, 3) == 1:
            self.assigned_to = taskgroup.user_set.all().order_by("?").first()

        self.save()

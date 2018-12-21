from django import forms
from django.contrib.auth.models import Group
from django.forms import ModelForm
from todo.models import Task, TaskList


class AddTaskListForm(ModelForm):
    """The picklist showing allowable groups to which a new list can be added
    determines which groups the user belongs to. This queries the form object
    to derive that list."""

    def __init__(self, user, *args, **kwargs):
        super(AddTaskListForm, self).__init__(*args, **kwargs)
        self.fields["group"].queryset = Group.objects.filter(user=user)
        self.fields["group"].widget.attrs = {
            "id": "id_group",
            "class": "custom-select mb-3",
            "name": "group",
        }

    class Meta:
        model = TaskList
        exclude = ["created_date", "slug"]


class AddEditTaskForm(ModelForm):
    """The picklist showing the users to which a new task can be assigned
    must find other members of the group this TaskList is attached to."""

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        task_list = kwargs.get("initial").get("task_list")
        members = task_list.group.user_set.all()
        self.fields["assigned_to"].queryset = members
        self.fields["assigned_to"].label_from_instance = lambda obj: "%s (%s)" % (
            obj.get_full_name(),
            obj.username,
        )
        self.fields["assigned_to"].widget.attrs = {
            "id": "id_assigned_to",
            "class": "custom-select mb-3",
            "name": "assigned_to",
        }
        self.fields["task_list"].value = kwargs["initial"]["task_list"].id

    due_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), required=False)

    title = forms.CharField(widget=forms.widgets.TextInput())

    note = forms.CharField(widget=forms.Textarea(), required=False)

    class Meta:
        model = Task
        exclude = []


class AddExternalTaskForm(ModelForm):
    """Form to allow users who are not part of the GTD system to file a ticket."""

    title = forms.CharField(widget=forms.widgets.TextInput(attrs={"size": 35}), label="Summary")
    note = forms.CharField(widget=forms.widgets.Textarea(), label="Problem Description")
    priority = forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        model = Task
        exclude = (
            "task_list",
            "created_date",
            "due_date",
            "created_by",
            "assigned_to",
            "completed",
            "completed_date",
        )


class SearchForm(forms.Form):
    """Search."""

    q = forms.CharField(widget=forms.widgets.TextInput(attrs={"size": 35}))

from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import Group
from todo.models import Item, TaskList
from django.contrib.auth import get_user_model


class AddTaskListForm(ModelForm):
    """The picklist showing allowable groups to which a new list can be added
    determines which groups the user belongs to. This queries the form object
    to derive that list."""

    def __init__(self, user, *args, **kwargs):
        super(AddTaskListForm, self).__init__(*args, **kwargs)
        self.fields['group'].queryset = Group.objects.filter(user=user)

    class Meta:
        model = TaskList
        exclude = []


class AddEditItemForm(ModelForm):
    """The picklist showing the users to which a new task can be assigned
    must find other members of the groups the current list belongs to."""

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = get_user_model().objects.filter(groups__in=user.groups.all())
        self.fields['assigned_to'].label_from_instance = lambda obj: "%s (%s)" % (obj.get_full_name(), obj.username)
        self.fields['assigned_to'].widget.attrs = {
            'id': 'id_assigned_to', 'class': "custom-select mb-3", 'name': 'assigned_to'}
        self.fields['task_list'].value = kwargs['initial']['task_list'].id

    due_date = forms.DateField(
            widget=forms.DateInput(attrs={'type': 'date'}), required=False)

    title = forms.CharField(
        widget=forms.widgets.TextInput())

    note = forms.CharField(
        widget=forms.Textarea(), required=False)

    class Meta:
        model = Item
        exclude = []


class AddExternalItemForm(ModelForm):
    """Form to allow users who are not part of the GTD system to file a ticket."""

    title = forms.CharField(
        widget=forms.widgets.TextInput(attrs={'size': 35}),
        label="Summary"
    )
    note = forms.CharField(
        widget=forms.widgets.Textarea(),
        label='Problem Description',
    )
    priority = forms.IntegerField(
        widget=forms.HiddenInput(),
    )

    class Meta:
        model = Item
        exclude = (
            'task_list', 'created_date', 'due_date', 'created_by', 'assigned_to', 'completed', 'completed_date', )


class SearchForm(forms.Form):
    """Search."""

    q = forms.CharField(
        widget=forms.widgets.TextInput(attrs={'size': 35})
    )

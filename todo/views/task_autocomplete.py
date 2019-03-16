from dal import autocomplete
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from todo.models import Task
from todo.utils import user_can_read_task


class TaskAutocomplete(autocomplete.Select2QuerySetView):
    @method_decorator(login_required)
    def dispatch(self, request, task_id, *args, **kwargs):
        self.task = get_object_or_404(Task, pk=task_id)
        if not user_can_read_task(self.task, request.user):
            raise PermissionDenied

        return super().dispatch(request, task_id, *args, **kwargs)

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Task.objects.none()

        qs = Task.objects.filter(task_list=self.task.task_list).exclude(pk=self.task.pk)

        if self.q:
            qs = qs.filter(title__istartswith=self.q)

        return qs

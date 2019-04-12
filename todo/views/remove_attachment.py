from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from todo.models import Attachment
from todo.utils import remove_attachment_file


@login_required
def remove_attachment(request, attachment_id: int) -> HttpResponse:
    """Delete a previously posted attachment object and its corresponding file
    from the filesystem, permissions allowing.
    """

    if request.method == "POST":
        attachment = get_object_or_404(Attachment, pk=attachment_id)

        redir_url = reverse("todo:task_detail", kwargs={"task_id": attachment.task.id})

        # Permissions
        if not (
            attachment.task.task_list.group in request.user.groups.all()
            or request.user.is_superuser
        ):
            raise PermissionDenied

        if remove_attachment_file(attachment.id):
            messages.success(request, f"Attachment {attachment.id} removed.")
        else:
            messages.error(
                request, f"Sorry, there was a problem deleting attachment {attachment.id}."
            )

        return redirect(redir_url)

    else:
        raise PermissionDenied

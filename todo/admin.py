import csv
import datetime

from django.contrib import admin
from django.http import HttpResponse

from todo.models import Attachment, Comment, Task, TaskList


def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    content_disposition = f"attachment; filename={opts.verbose_name}.csv"
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = content_disposition
    writer = csv.writer(response)
    fields = [
        field for field in opts.get_fields() if not (field.many_to_many and not field.one_to_many)
    ]
    # Write a first row with header information
    writer.writerow([field.verbose_name for field in fields])
    # Write data rows
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime("%d/%m/%Y")
            data_row.append(value)
        writer.writerow(data_row)
    return response


export_to_csv.short_description = "Export to CSV"


class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "task_list", "completed", "priority", "due_date")
    list_filter = ("task_list",)
    ordering = ("priority",)
    search_fields = ("title",)
    actions = [export_to_csv]


class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "date", "snippet")


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("task", "added_by", "timestamp", "file")
    autocomplete_fields = ["added_by", "task"]


admin.site.register(TaskList)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Attachment, AttachmentAdmin)

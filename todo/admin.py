from django.contrib import admin

from todo.models import Attachment, Comment, Task, TaskList


class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "task_list", "completed", "priority", "due_date")
    list_filter = ("task_list",)
    ordering = ("priority",)
    search_fields = ("title",)


class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "date", "snippet")


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("task", "added_by", "timestamp", "file")
    autocomplete_fields = ["added_by", "task"]


admin.site.register(TaskList)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Attachment, AttachmentAdmin)

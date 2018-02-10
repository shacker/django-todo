from django.contrib import admin
from todo.models import Item, TaskList, Comment


class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'task_list', 'completed', 'priority', 'due_date')
    list_filter = ('task_list',)
    ordering = ('priority',)
    search_fields = ('name',)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'date', 'snippet')


admin.site.register(TaskList)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Item, ItemAdmin)

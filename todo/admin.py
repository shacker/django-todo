from django.contrib import admin
from todo.models import Item, List, Comment


class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'list', 'priority', 'due_date')
    list_filter = ('list',)
    ordering = ('priority',)
    search_fields = ('name',)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'date', 'snippet')


admin.site.register(List)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Item, ItemAdmin)

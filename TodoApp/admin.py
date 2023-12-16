from django.contrib import admin
from .models import Task

class TaskAdmin(admin.ModelAdmin):
    list_display = ('task_id', 'title', 'timestamp', 'due_date', 'status')
    list_filter = ('status', 'timestamp', 'due_date')
    search_fields = ('title', 'description', 'tags')

    fieldsets = (
        ('Task Information', {
            'fields': ('title', 'description', 'due_date', 'tags', 'status'),
        }),
        ('Timestamp Information', {
            'fields': ('timestamp',),
            'classes': ('collapse',),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj:
            return readonly_fields + ('timestamp',)
        return readonly_fields

admin.site.register(Task, TaskAdmin)

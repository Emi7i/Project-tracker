from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'project_type', 'due_date', 'next_task', 'created_at']
    list_filter = ['project_type', 'due_date']
    search_fields = ['name']

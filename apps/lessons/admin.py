from django.contrib import admin
from .models import Lesson

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_approved', 'created_at', 'updated_at')
    list_filter = ('is_approved',)
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('uid', 'created_at', 'updated_at')

    class Media:
        css = {"all": ("lessons/admin_prose_editor.css",)}

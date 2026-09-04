from django.contrib import admin
from django import forms
from django_ace import AceWidget
from .models import Problem, Category, ProblemAttempt


class CategoryModeSelect(forms.Select):
    """Select widget that stamps each <option> with the category's Ace mode
    so admin_mode_switcher.js can read it via data-ace-mode, instead of
    re-deriving the mode from the category's display name in JS."""
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value:
            pk = value.value if hasattr(value, 'value') else value
            ace_mode = Category.objects.filter(pk=pk).values_list('ace_mode', flat=True).first()
            if ace_mode:
                option['attrs']['data-ace-mode'] = ace_mode
        return option


class ProblemAdminForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = '__all__'
        widgets = {
            'category': CategoryModeSelect(),
            'solution': AceWidget(
                mode='text',  # real mode is set client-side by admin_mode_switcher.js
                theme='monokai',
                width='100%',
                height='400px',
                showprintmargin=False,
                tabsize=4,
                attrs={'class': 'ace-editor-area'}
            ),
            # 'description' is intentionally omitted here — ProseEditorField
            # supplies its own widget via formfield(), same as on Lesson.
        }


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'ace_mode')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    form = ProblemAdminForm
    list_display = ('title', 'category', 'created_at')
    list_filter = ('category',)
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}

    class Media:
        css = {
            'all': ('lessons/admin_prose_editor.css',)  # height-cap override for .ProseMirror
        }
        js = ('js/admin_mode_switcher.js',)


@admin.register(ProblemAttempt)
class ProblemAttemptAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'problem', 'solve_count', 'correct_streak', 'next_review_date', 'last_solved',
    )
    list_filter = ('correct_streak', 'next_review_date')
    search_fields = ('user__username', 'problem__title')
    autocomplete_fields = ('user', 'problem')
    date_hierarchy = 'next_review_date'
    readonly_fields = ('solve_count', 'correct_streak', 'next_review_date', 'last_solved')
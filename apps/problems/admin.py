from django.contrib import admin
from .models import Problem, Category 
from django_ace import AceWidget 
from django import forms 

class ProblemAdminForm(forms.ModelForm):
    class Meta:
        model = Problem 
        fields = '__all__'
        widgets = {
            'solution': AceWidget(
                mode='c_cpp',
                theme='monokai',
                width='100%',
                height='400px',
                showprintmargin=False,
                tabsize=4,
            ),
        }

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    form = ProblemAdminForm 
    list_display = ('title', 'category', 'created_at')
    list_filter = ('category',)
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
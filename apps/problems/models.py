from django.db import models, transaction
from django.utils.text import slugify
from apps.core.models import BaseModel
from django.conf import settings
from django_prose_editor.fields import ProseEditorField


class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    ace_mode = models.CharField(
        max_length=50,
        choices=[
            ('python', 'Python'), ('c_cpp', 'C / C++'), ('javascript', 'JavaScript'),
            ('java', 'Java'), ('csharp', 'C#'), ('mysql', 'MySQL'),
            ('golang', 'Go'), ('ruby', 'Ruby'), ('text', 'Plain Text'),
        ],
        default='text',
    )

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Problem(BaseModel):
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='problems'
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = ProseEditorField(
        extensions={
            "Bold": True,
            "Italic": True,
            "Strike": True,
            "BulletList": True,
            "OrderedList": True,
            "ListItem": True,
            "Blockquote": True,
            "CodeBlock": True,
            "Heading": {"levels": [2, 3]},
            "Link": True,
            "HorizontalRule": True,
            "History": True,
        },
        sanitize=True,
    )
    solution = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        if not self.pk:
            if Problem.objects.filter(order=self.order).exists():
                with transaction.atomic():
                    Problem.objects.filter(order__gte=self.order).update(order=models.F('order') + 1)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ProblemAttempt(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    problem = models.ForeignKey('Problem', on_delete=models.CASCADE)
    solve_count = models.PositiveIntegerField(default=0)
    last_solved = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'problem')

    def __str__(self):
        return f"{self.user.username} - {self.problem.title} - {self.solve_count}"
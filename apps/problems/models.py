from django.db import models, transaction
from django.utils.text import slugify
from apps.core.models import BaseModel
from django.conf import settings
from django_prose_editor.fields import ProseEditorField
from datetime import timedelta
from django.utils import timezone
from .utils.spaced_repetition import get_next_interval_days


class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Language(BaseModel):
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

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Problem(BaseModel):
    language = models.ForeignKey(
        Language,
        on_delete=models.PROTECT,
        related_name='problems',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
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
            "Table": True,
            "TableRow": True,
            "TableHeader": True,
            "TableCell": True,
        },
        sanitize=True,
    )
    solution = models.TextField()
    order = models.PositiveIntegerField(default=0)

    PROBLEM_TYPE_CHOICES = [
        ('code', 'Code Recall'),
        ('sql', 'SQL Query'),
    ]
    problem_type = models.CharField(max_length=10, choices=PROBLEM_TYPE_CHOICES, default='code')
    order_matters = models.BooleanField(
        default=False,
        help_text="If True, row order in SQL results must match reference_query exactly"
    )

    class Meta:
        ordering = ['language', 'category', 'order']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        needs_order = not self.pk

        if self.pk:
            old_language_id, old_category_id = Problem.objects.filter(
                pk=self.pk
            ).values_list('language_id', 'category_id').first()

            if old_language_id != self.language_id or old_category_id != self.category_id:
                needs_order = True

        if needs_order:
            last_order = Problem.objects.filter(
                language=self.language, category=self.category
            ).exclude(pk=self.pk).aggregate(models.Max('order'))['order__max']
            self.order = 0 if last_order is None else last_order + 1

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ProblemAttemptManager(models.Manager):
    def due_for_review(self, user):
        today = timezone.now().date()
        return self.filter(user=user, next_review_date__lte=today).select_related('problem')


class ProblemAttempt(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    problem = models.ForeignKey('Problem', on_delete=models.CASCADE)
    solve_count = models.PositiveIntegerField(default=0)
    correct_streak = models.PositiveIntegerField(default=0)
    next_review_date = models.DateField(null=True, blank=True, db_index=True)
    last_solved = models.DateTimeField(auto_now=True)

    objects = ProblemAttemptManager()

    class Meta:
        unique_together = ('user', 'problem')

    def record_attempt(self, is_correct: bool) -> None:
        """Update streak, solve_count, and schedule the next review date.

        Call this once per submission, after your existing correctness
        check determines is_correct — this method owns nothing about
        *how* correctness is judged, only what happens to the review
        schedule afterward.
        """
        if is_correct:
            self.solve_count += 1
            self.correct_streak += 1
        else:
            self.correct_streak = 0

        interval_days = get_next_interval_days(self.correct_streak)
        self.next_review_date = timezone.now().date() + timedelta(days=interval_days)
        self.save()

    def __str__(self):
        return f"{self.user.username} - {self.problem.title} - {self.solve_count}"
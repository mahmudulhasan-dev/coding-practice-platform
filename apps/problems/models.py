from django.db import models, transaction
from django.utils.text import slugify 
from apps.core.models import BaseModel 
from django.conf import settings 

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
    
class Problem(BaseModel):
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='problems'
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
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

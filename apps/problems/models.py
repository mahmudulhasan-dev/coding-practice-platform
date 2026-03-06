from django.db import models, transaction
from django.utils.text import slugify 
from apps.core.models import BaseModel 

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

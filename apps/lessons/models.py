from django.db import models
from django.urls import reverse
from apps.core.models import BaseModel

class Lesson(BaseModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    is_approved = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('lessons:lesson_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

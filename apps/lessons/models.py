from django.db import models
from django.urls import reverse
from apps.core.models import BaseModel
from django_prose_editor.fields import ProseEditorField

class Lesson(BaseModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    content = ProseEditorField(
        extensions={
            "Bold": True,
            "Italic": True,
            "Strike": True,
            "Underline": True,
            "Heading": {"levels": [2, 3, 4]},   # h1 reserved for lesson.title in the template
            "BulletList": True,
            "OrderedList": True,
            "ListItem": True,
            "Blockquote": True,
            "CodeBlock": True,
            "Link": True,
            "HorizontalRule": True,
            "History": True,
        },
        sanitize=True,
    )
    is_approved = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('lessons:lesson_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

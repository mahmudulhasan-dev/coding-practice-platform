from django.shortcuts import get_object_or_404, render
from .models import Lesson


def lesson_list(request):
    lessons = Lesson.objects.all().order_by('title')
    return render(request, 'lessons/lesson_list.html', {'lessons': lessons})


def lesson_detail(request, slug):
    lesson = get_object_or_404(Lesson, slug=slug)
    return render(request, 'lessons/lesson_detail.html', {'lesson': lesson})
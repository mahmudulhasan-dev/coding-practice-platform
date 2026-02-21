from django.shortcuts import render, get_object_or_404 
from .models import Problem, Category 

def problem_list(request):
    categories = Category.objects.prefetch_related('problems').all()
    return render(request, 'problems/dashboard.html', {'categories': categories})

def problem_detail(request, slug):
    problem = get_object_or_404(Problem, slug=slug)
    show_solution = False 
    user_input = ""

    if request.method == "POST":
        user_input = request.POST.get('user_answer')
        show_solution = True 

    return render(request, 'problems/practice_room.html', {
        'problem': problem,
        'show_solution': show_solution,
        'user_input': user_input 
    })

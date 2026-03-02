from django.shortcuts import render, get_object_or_404 
from .models import Problem, Category 

def problem_list(request):
    categories = Category.objects.prefetch_related('problems').all()
    return render(request, 'problems/dashboard.html', {'categories': categories})

def problem_detail(request, slug):
    problem = get_object_or_404(Problem, slug=slug)
    show_solution = False 
    user_input = ""
    feedback = ""
    is_correct = False

    if request.method == "POST":
        user_input = request.POST.get('user_answer')
        if user_input.strip() == problem.solution.strip():
            feedback = "Correct!"
            is_correct = True
        else:
            feedback = "Incorrect solution."
        
        show_solution = True 

    return render(request, 'problems/practice_room.html', {
        'problem': problem,
        'show_solution': show_solution,
        'user_input': user_input,
        'feedback': feedback,
        'is_correct': is_correct
    })

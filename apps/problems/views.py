from django.shortcuts import render, get_object_or_404 
from .models import Problem, Category, ProblemAttempt 
import difflib 
from django.db.models import F 
from .utils.code_normalizer import normalize_code

def problem_list(request):
    categories = Category.objects.prefetch_related('problems').all()
    return render(request, 'problems/dashboard.html', {'categories': categories})

def problem_detail(request, slug):
    problem = get_object_or_404(Problem, slug=slug)
    user_input = ""
    feedback = ""
    is_correct = False
    diff_results = None 

    if request.method == "POST":
        user_input = request.POST.get('user_answer', '')
        if normalize_code(user_input) == normalize_code(problem.solution):
            feedback = "Correct!"
            is_correct = True

            if request.user.is_authenticated:
                attempt, created = ProblemAttempt.objects.get_or_create(
                    user=request.user,
                    problem=problem
                )
                attempt.solve_count = F('solve_count') + 1
                attempt.save()
        else:
            feedback = "Incorrect solution."
        
        diff_results = difflib.HtmlDiff().make_table(
            fromlines=problem.solution.splitlines(),
            tolines=user_input.splitlines(),
            fromdesc="Correct Solution",
            todesc="Your logic"
        )

    return render(request, 'problems/practice_room.html', {
        'problem': problem,
        'user_input': user_input,
        'feedback': feedback,
        'is_correct': is_correct,
        'diff_results': diff_results,
    })

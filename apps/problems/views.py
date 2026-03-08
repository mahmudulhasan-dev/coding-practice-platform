from django.shortcuts import render, get_object_or_404 
from .models import Problem, Category, ProblemAttempt 
import re 
import difflib 
from django.db.models import F 

def normalize_code(code_string):
    if not code_string:
        return ""
    code = code_string
    code = code.replace('\r\n', '\n').replace('\r', '\n')
    code = re.sub(r'\s+', '', code)
    return code 

def problem_list(request):
    categories = Category.objects.prefetch_related('problems').all()
    return render(request, 'problems/dashboard.html', {'categories': categories})

def problem_detail(request, slug):
    problem = get_object_or_404(Problem, slug=slug)
    show_solution = False 
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
            diff = difflib.HtmlDiff().make_table(
                fromlines=problem.solution.splitlines(),
                tolines=user_input.splitlines(),
                fromdesc="Correct Solution",
                todesc="Your logic"
            )
            diff_results = diff 
        
        show_solution = True 

    return render(request, 'problems/practice_room.html', {
        'problem': problem,
        'show_solution': show_solution,
        'user_input': user_input,
        'feedback': feedback,
        'is_correct': is_correct,
        'diff_results': diff_results,
    })

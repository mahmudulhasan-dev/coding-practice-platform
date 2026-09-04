from django.shortcuts import render, get_object_or_404
from .models import Problem, Category, ProblemAttempt
from .utils.code_normalizer import normalize_code
from .utils.diff_builder import build_line_diff


def problem_list(request):
    categories = Category.objects.prefetch_related('problems').all()
    due_attempts = []
    if request.user.is_authenticated:
        due_attempts = ProblemAttempt.objects.due_for_review(request.user)

    return render(request, 'problems/dashboard.html', {
        'categories': categories,
        'due_attempts': due_attempts,
    })


def problem_detail(request, slug):
    problem = get_object_or_404(Problem, slug=slug)
    user_input = ""
    feedback = ""
    is_correct = False
    diff_rows = None

    if request.method == "POST":
        user_input = request.POST.get('user_answer', '')
        is_correct = normalize_code(user_input) == normalize_code(problem.solution)
        feedback = "Correct!" if is_correct else "Incorrect solution."

        if request.user.is_authenticated:
            attempt, _ = ProblemAttempt.objects.get_or_create(
                user=request.user,
                problem=problem
            )
            attempt.record_attempt(is_correct)

        diff_rows = build_line_diff(problem.solution, user_input)

    return render(request, 'problems/practice_room.html', {
        'problem': problem,
        'user_input': user_input,
        'feedback': feedback,
        'is_correct': is_correct,
        'diff_rows': diff_rows,
    })
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Problem, Category, ProblemAttempt
from .utils.code_normalizer import normalize_code
from .utils.diff_builder import build_line_diff


def _attach_review_status(categories, user):
    """"
    Annotate each prefetched Problem with review_status_label/_class
    based on the user's ProblemAttempt, if any. Mutates the already loaded
    Problem instances in place so the template can keep using
    category.problems.all() unchanged.
    """
    today = timezone.now().date()
    attempts_by_problem_id = {}
    if user.is_authenticated:
        attempts_by_problem_id = {
            a.problem_id: a
            for a in ProblemAttempt.objects.filter(user=user)
        }

    for category in categories:
        for problem in category.problems.all():
            attempt = attempts_by_problem_id.get(problem.id)

            if attempt is None:
                label, css_class = "Not Attempted", "bg-secondary"
            elif attempt.next_review_date and attempt.next_review_date <= today:
                label, css_class = "Due for Review", "bg-warning text-dark"
            elif attempt.correct_streak == 0:
                label = f"Retry {attempt.next_review_date:%b %d}"
                css_class = "bg-danger"
            else:
                label = f"Next Review {attempt.next_review_date:%b %d}"
                css_class = "bg-success"

            problem.review_status_label = label
            problem.review_status_class = css_class


def problem_list(request):
    categories = Category.objects.prefetch_related('problems').all()
    _attach_review_status(categories, request.user)
    
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
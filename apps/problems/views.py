from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Problem, Category, ProblemAttempt, Language
from .utils.code_normalizer import normalize_code
from .utils.diff_builder import build_line_diff
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .utils.sql_sandbox import run_sandboxed_query, UnsafeQueryError


def _attach_review_status(languages, user):
    """"
    Annotate each prefetched Problem with review_status_label/_class
    based on the user's ProblemAttempt, if any. Mutates the already loaded
    Problem instances in place so the template can keep using
    language.problems.all() unchanged.
    """
    today = timezone.now().date()
    attempts_by_problem_id = {}
    if user.is_authenticated:
        attempts_by_problem_id = {
            a.problem_id: a
            for a in ProblemAttempt.objects.filter(user=user)
        }

    for language in languages:
        for problem in language.problems.all():
            attempt = attempts_by_problem_id.get(problem.id)

            if attempt is None or attempt.next_review_date is None:
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
    languages = Language.objects.prefetch_related(
        Prefetch('problems', queryset=Problem.objects.select_related('category').order_by('category', 'order'))
        ).all()
    _attach_review_status(languages, request.user)

    for language in languages:
        categories = {}
        for problem in language.problems.all():
            categories.setdefault(problem.category, []).append(problem)
        language.grouped_categories = [
            {'category': category, 'problems': problems}
            for category, problems in categories.items()
        ]

    due_attempts = []
    if request.user.is_authenticated:
        due_attempts = ProblemAttempt.objects.due_for_review(request.user)

    return render(request, 'problems/dashboard.html', {
        'languages': languages,
        'due_attempts': due_attempts,
    })


def problem_detail(request, slug):
    problem = get_object_or_404(Problem, slug=slug)
    user_input = ""
    feedback = ""
    is_correct = False
    diff_rows = None
    sql_columns = None
    sql_rows = None
    next_problem = None

    if request.method == "POST":
        user_input = request.POST.get('user_answer', '')

        if problem.problem_type == "sql":
            try:
                user_columns, user_rows = run_sandboxed_query(user_input)
                expected_columns, expected_rows = run_sandboxed_query(problem.solution)
                is_correct = (
                    user_columns == expected_columns
                    and (user_rows == expected_rows if problem.order_matters
                         else set(user_rows) == set(expected_rows))
                )
                sql_columns, sql_rows = user_columns, user_rows
                feedback = "Correct!" if is_correct else "Incorrect result set."
            except UnsafeQueryError as e:
                is_correct = False
                feedback = str(e)
        else:
            is_correct = normalize_code(user_input) == normalize_code(problem.solution)
            feedback = "Correct!" if is_correct else "Incorrect solution."
            diff_rows = build_line_diff(problem.solution, user_input)

        if request.user.is_authenticated:
            attempt, _ = ProblemAttempt.objects.get_or_create(
                user=request.user,
                problem=problem
            )
            attempt.record_attempt(is_correct)

        next_problem = (
            Problem.objects
            .filter(category=problem.category, order__gt=problem.order)
            .order_by('order')
            .first()
            )

    return render(request, 'problems/practice_room.html', {
        'problem': problem,
        'user_input': user_input,
        'feedback': feedback,
        'is_correct': is_correct,
        'diff_rows': diff_rows,
        'sql_columns': sql_columns,
        'sql_rows': sql_rows,
        'next_problem': next_problem,
    })


@require_POST
def run_sql_submission(request, problem_id):
    problem = get_object_or_404(Problem, pk=problem_id)
    user_sql = request.POST.get("query", "")

    try:
        columns, rows = run_sandboxed_query(user_sql)
    except UnsafeQueryError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        # MariaDB raises on timeout / syntax errors — surface a clean message
        return JsonResponse({"error": "Query failed: " + str(e)}, status=400)

    expected_columns, expected_rows = run_sandboxed_query(problem.solution)

    is_correct = (
        columns == expected_columns
        and (rows == expected_rows if problem.order_matters else set(rows) == set(expected_rows))
    )

    return JsonResponse({
        "columns": columns,
        "rows": rows,
        "is_correct": is_correct,
    })
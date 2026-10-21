from django.db.models import Count
from .models import AttemptLog, PracticeRun


def first_try_rate(user):
    runs = PracticeRun.objects.filter(user=user, solved_at__isnull=False).annotate(n=Count('logs'))
    total = runs.count()
    return runs.filter(n=1).count() / total if total else 0.0


def mistake_breakdown(user):
    return (AttemptLog.objects.filter(user=user, is_correct=False)
            .exclude(mistake_reason='')
            .values('mistake_reason').annotate(n=Count('id')).order_by('-n'))
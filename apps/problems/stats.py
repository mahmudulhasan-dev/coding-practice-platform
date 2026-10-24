from django.db.models import Count
from .models import AttemptLog, PracticeRun


def first_try_rate(user):
    scored = AttemptLog.objects.filter(user=user, is_scored=True)
    total = scored.count()
    return scored.filter(is_correct=True).count() / total if total else 0.0


def mistake_breakdown(user):
    return (AttemptLog.objects.filter(user=user, is_correct=False)
            .exclude(mistake_reason='')
            .values('mistake_reason').annotate(n=Count('id')).order_by('-n'))
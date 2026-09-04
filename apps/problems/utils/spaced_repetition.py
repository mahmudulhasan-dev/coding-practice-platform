"""Fixed-interval spaced repetition schedule for problem review.

Interval (in days) is selected by the user's current correct streak on a
problem. An incorrect submission resets the streak to 0 and the problem
comes back the next day. Streak beyond the schedule length caps at the
final interval (60 days) rather than growing indefinitely.
"""

REVIEW_INTERVALS_DAYS = [3, 7, 15, 30, 60]
INCORRECT_INTERVAL_DAYS = 1


def get_next_interval_days(correct_streak: int) -> int:
    """Return the number of days until the next review.

    correct_streak=0 means the most recent submission was incorrect (or
    this is the very first attempt) -> review tomorrow.
    correct_streak=1 -> first correct answer -> 3 days.
    correct_streak=2 -> second correct in a row -> 7 days.
    ...continues up the schedule, capping at 60 days once the streak
    exceeds the schedule length.
    """
    if correct_streak <= 0:
        return INCORRECT_INTERVAL_DAYS
    index = min(correct_streak - 1, len(REVIEW_INTERVALS_DAYS) - 1)
    return REVIEW_INTERVALS_DAYS[index]
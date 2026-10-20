from difflib import SequenceMatcher


def guess_reason(submitted: str, solution: str) -> str:
    a, b = submitted.strip(), solution.strip()
    matcher = SequenceMatcher(None, a, b)
    changed = sum(
        max(i2 - i1, j2 - j1)
        for tag, i1, i2, j1, j2 in matcher.get_opcodes() if tag != 'equal'
    )
    ratio = matcher.ratio()
    if ratio >= 0.95 and changed <= 3:
        return 'typo'
    if ratio < 0.5:
        return 'forgot'
    return ''
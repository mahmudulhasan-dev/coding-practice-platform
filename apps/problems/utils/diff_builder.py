import re
from difflib import SequenceMatcher


def _normalize_line(line: str) -> str:
    """Collapse internal whitespace so cosmetic-only diffs (spacing,
    tabs) don't get flagged as logic changes."""
    return re.sub(r'\s+', ' ', line.strip())


def _is_blank(line: str | None) -> bool:
    return line is None or line.strip() == ''


def build_line_diff(correct: str, user: str):
    """
    Build an aligned, line-level diff between the correct solution and
    the user's submission.

    Returns a list of row dicts:
        {
            'tag': 'equal' | 'replace' | 'insert' | 'delete',
            'left': str or None,      # correct solution line
            'right': str or None,     # user's line
            'left_no': int or None,   # 1-based line number, left side
            'right_no': int or None,  # 1-based line number, right side
        }

    Rows are padded so left/right stay visually aligned row-for-row,
    even when a line only exists on one side (GitHub split-diff style).
    Whitespace-only differences within a changed block are downgraded
    to 'equal', and insert/delete rows whose only content is a blank
    line are dropped entirely — blank lines carry no logic difference,
    so they shouldn't compete visually with real changes.
    """
    correct_lines = correct.splitlines() if correct else []
    user_lines = user.splitlines() if user else []

    normalized_correct = [_normalize_line(l) for l in correct_lines]
    normalized_user = [_normalize_line(l) for l in user_lines]

    matcher = SequenceMatcher(None, normalized_correct, normalized_user, autojunk=False)

    rows = []
    left_no = 0
    right_no = 0

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        left_block = correct_lines[i1:i2]
        right_block = user_lines[j1:j2]
        max_len = max(len(left_block), len(right_block))

        for k in range(max_len):
            left_line = left_block[k] if k < len(left_block) else None
            right_line = right_block[k] if k < len(right_block) else None

            if left_line is None:
                row_tag = 'insert'
            elif right_line is None:
                row_tag = 'delete'
            elif tag == 'replace':
                row_tag = 'equal' if _normalize_line(left_line) == _normalize_line(right_line) else 'replace'
            else:
                row_tag = tag  # 'equal'

            if left_line is not None:
                left_no += 1
            if right_line is not None:
                right_no += 1

            # Skip insert/delete rows that are just a blank line on the
            # populated side — no logic content to show the student.
            if row_tag in ('insert', 'delete'):
                populated = right_line if row_tag == 'insert' else left_line
                if _is_blank(populated):
                    continue

            rows.append({
                'tag': row_tag,
                'left': left_line,
                'right': right_line,
                'left_no': left_no if left_line is not None else None,
                'right_no': right_no if right_line is not None else None,
            })

    return rows
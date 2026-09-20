import sqlparse
from django.db import connections
from sqlparse.tokens import DDL, DML
from sqlparse.sql import Parenthesis

TIMEOUT_MS = 2000
FORBIDDEN_DML = {"INSERT", "UPDATE", "DELETE", "REPLACE"}
FORBIDDEN_DDL = {"DROP", "ALTER", "CREATE", "TRUNCATE", "GRANT", "RENAME"}

class UnsafeQueryError(ValueError):
    pass


def _first_real_token(stmt):
    """Unwrap leading Parenthesis groups (e.g. '(SELECT ...) UNION (SELECT ...)')
    to find the statement's actual leading keyword."""
    tok = stmt.token_first(skip_cm=True)
    while isinstance(tok, Parenthesis):
        open_paren = tok.token_first(skip_cm=True)
        idx = tok.token_index(open_paren)
        tok = tok.token_next(idx, skip_cm=True)[1]
    return tok


def validate_select_only(sql: str) -> str:
    """Raises UnsafeQueryError unless sql is a single SQL statement that only reads 
    data (SELECT, optionally combining multiple SELECTs via UNION/INTERSECT/EXCEPT — 
    parenthesized branches included)."""

    statements = [s for s in sqlparse.parse(sql) if s.token_first(skip_cm=True)]
    if len(statements) != 1:
        raise UnsafeQueryError("Submit exactly one SQL statement.")

    stmt = statements[0]
    first_token = _first_real_token(stmt)

    if first_token is None or first_token.ttype is not DML or first_token.value.upper() != "SELECT":
        raise UnsafeQueryError("Only SELECT statements are allowed.")

    for token in stmt.flatten():
        if token.ttype is DDL:
            raise UnsafeQueryError("DDL statements are not allowed.")
        if token.ttype is DML and token.value.upper() in FORBIDDEN_DML:
            raise UnsafeQueryError("Only SELECT statements are allowed.")

    # strip a single trailing semicolon; reject any semicolon mid-string (stacked queries)
    cleaned = sql.strip()
    if cleaned.count(";") > 1 or (";" in cleaned and not cleaned.rstrip().endswith(";")):
        raise UnsafeQueryError("Multiple statements are not allowed.")

    return cleaned.rstrip(";")


def run_sandboxed_query(sql: str):
    """Returns (columns, rows) or raises on DB error/timeout."""
    clean_sql = validate_select_only(sql)

    with connections["sql_sandbox"].cursor() as cursor:
        cursor.execute(f"SET STATEMENT max_statement_time={TIMEOUT_MS} FOR {clean_sql}")
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return columns, rows


def compare_query_results(user_sql: str, problem) -> dict:
    """Runs user_sql and problem.solution, returns comparison result."""
    user_columns, user_rows = run_sandboxed_query(user_sql)
    expected_columns, expected_rows = run_sandboxed_query(problem.solution)
    is_correct = (
        user_columns == expected_columns
        and (user_rows == expected_rows if problem.order_matters
             else set(user_rows) == set(expected_rows))
    )
    return {
        "columns": user_columns,
        "rows": user_rows,
        "is_correct": is_correct,
    }
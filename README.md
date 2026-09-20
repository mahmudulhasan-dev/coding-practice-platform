# Coding Practice Platform

A Django-based platform I built for myself to keep my algorithm/coding and SQL knowledge sharp — and actually *checked*, not just practiced once and forgotten. The core mechanic is spaced-repetition recall: solve a problem, get scheduled to revisit it later, and track whether you still remember it.

> **Note:** This is a personal-use tool without public sign-up yet — there's intentionally no register/login flow. It's built for my own daily practice, not as a multi-user product (yet).

## What it does

- **Code recall problems** — solve a problem, get a line-by-line diff against the reference solution, and track correctness over time via spaced repetition (fixed review intervals: 1/3/7/15/30/60 days).
- **SQL problems** — write a query against a sandboxed database, get your query's actual result set back, and get graded by comparing result sets (not text) against a reference solution. Handles queries where row order matters and where it doesn't.
- **Lessons** — my own running notes on each topic, written up as I go and kept in the platform alongside the problems, with code-block syntax highlighting.
- **Spaced repetition dashboard** — see what's due for review, track streaks per problem.

## Stack

- **Backend:** Django
- **Frontend:** Bootstrap 5, Ace editor, Prism.js, Django templates
- **Database:** MariaDB in production, SQLite for local default, MySQL via Docker as a local alternative
- **Hosting:** cPanel shared hosting

## Why SQL grading is interesting here

Most answer-checking on this platform is a text diff — does your code match the stored solution closely enough. That works for algorithms. It doesn't work for SQL: two correct queries can look nothing alike (different join order, aliases, `WHERE` vs `HAVING`).

So SQL problems are graded differently: the submitted query runs against a sandboxed database connection (a separate, SELECT-only MySQL user — not the app's main database), and the result set is compared against a reference query's result set. A query validator blocks anything that isn't a single `SELECT` statement, and a MariaDB statement-level timeout (`SET STATEMENT ... FOR`) prevents a runaway query from hanging a shared-hosting worker process.

## Status

Actively being built in public. Currently focused on the SQL problem-solving flow; UI polish and a public-facing version are on the roadmap but not yet a priority since this is primarily a personal tool right now.
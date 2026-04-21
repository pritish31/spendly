# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Activate the virtual environment first
source venv/bin/activate

# Run the app
python app.py          # starts on http://localhost:5001

# Run tests
pytest                 # all tests
pytest tests/test_foo.py::test_name   # single test
```

## Architecture

**Spendly** is a Flask + SQLite expense tracker built as a step-by-step learning project. Features are added incrementally — placeholder routes in `app.py` are stubs for future steps.

### Request flow

```
browser → app.py (route) → templates/*.html (Jinja2, extends base.html)
                         → database/db.py (SQLite via get_db())
```

### Key files

- `app.py` — all routes in one file; no blueprints
- `database/db.py` — must expose `get_db()`, `init_db()`, `seed_db()` (SQLite, row_factory, foreign keys on)
- `templates/base.html` — shared navbar and footer; all page templates extend this
- `static/css/style.css` — single stylesheet with CSS custom properties defined in `:root`; no CSS framework
- `static/js/main.js` — vanilla JS only; no libraries

### CSS conventions

All colours, spacing tokens, and font stacks are CSS variables in `:root` inside `style.css`. Use them (`var(--accent)`, `var(--ink)`, etc.) rather than hard-coded values. Page-specific styles that don't belong in the shared stylesheet go in a `{% block head %}` `<style>` tag in the template.

### Template conventions

Templates use `{% block head %}` for page-specific CSS, `{% block content %}` for the page body, and `{% block scripts %}` for page-specific JS. Inline `<script>` in `{% block scripts %}` is the accepted pattern for page-scoped JavaScript (see the video modal in `landing.html`).

### Auth forms

Login and register forms POST to `/login` and `/register`. Templates expect an optional `error` variable from the route for inline error display.

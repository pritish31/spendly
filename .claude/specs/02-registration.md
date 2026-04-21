# Spec: Registration

## Overview

This step implements user registration — the first point of account creation in Spendly. When a visitor submits the registration form, the app validates their input, hashes their password with Werkzeug, and inserts a new row into the `users` table. On success the user is redirected to the login page; on failure the form re-renders with an inline error message. This is a prerequisite for all authenticated features (login, profile, expenses).

## Depends on

- Step 01 — Database Setup (`users` table must exist via `init_db()`)

## Routes

| Method | Path | Description | Access |
|---|---|---|---|
| `GET` | `/register` | Render the registration form | Public |
| `POST` | `/register` | Process form submission, insert user, redirect | Public |

## Database changes

No new tables or columns. Uses the existing `users` table:

```
users(id, name, email, password_hash, created_at)
```

The `email` column already has a `UNIQUE` constraint — duplicate email attempts will raise an `IntegrityError` that must be caught and surfaced as a user-facing error.

## Templates

**Modify:**
- `templates/register.html` — form already renders; ensure it POSTs to `/register` and displays `{{ error }}` inline (pattern already present, just needs the route wired up)

## Files to change

- `app.py` — replace the stub `GET /register` with a combined GET/POST handler; add `redirect`, `url_for`, `request` to Flask imports; import `generate_password_hash` from `werkzeug.security`; import `get_db` from `database.db`

## Files to create

None.

## New dependencies

No new pip packages. `werkzeug` is already installed (it ships with Flask).

## Rules for implementation

- No SQLAlchemy or ORMs — use raw SQLite via `get_db()`
- Parameterised queries only — no f-strings or `%` formatting in SQL
- Passwords hashed with `werkzeug.security.generate_password_hash` — never store plaintext
- Use CSS variables — never hardcode hex values in templates or stylesheets
- All templates extend `base.html`
- Catch `sqlite3.IntegrityError` for duplicate email — show "An account with that email already exists."
- Validate that name, email, and password are all non-empty before attempting insert
- After successful insert, redirect to `/login` — do not auto-login (that comes in Step 3)

## Definition of done

- [ ] `GET /register` renders the registration form
- [ ] Submitting the form with valid name, email, and password inserts a new row into `users` and redirects to `/login`
- [ ] Submitting with an already-registered email re-renders the form with the error "An account with that email already exists."
- [ ] Submitting with any empty field re-renders the form with a validation error
- [ ] Password is never stored in plaintext — `password_hash` column contains a Werkzeug hash string
- [ ] Running `pytest` produces no errors

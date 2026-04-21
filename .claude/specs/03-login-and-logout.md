# Spec: Login and Logout

## Overview

This step implements session-based authentication for Spendly. When a user submits the login form, the app looks up their email in the `users` table, verifies the submitted password against the stored Werkzeug hash, and — on success — stores their `user_id` and `name` in a Flask server-side session. The `/logout` route clears the session and redirects to the landing page. Once this step is complete, all subsequent protected routes can gate access by checking `session.get('user_id')`.

## Depends on

- Step 01 — Database Setup (`users` table must exist via `init_db()`)
- Step 02 — Registration (users must exist in the database to log in)

## Routes

| Method | Path      | Description                                                | Access    |
| ------ | --------- | ---------------------------------------------------------- | --------- |
| `GET`  | `/login`  | Render the login form                                      | Public    |
| `POST` | `/login`  | Verify credentials, create session, redirect to `/profile` | Public    |
| `GET`  | `/logout` | Clear session, redirect to `/`                             | Logged-in |

## Database changes

No new tables or columns. Reads from the existing `users` table:

```
users(id, email, password_hash)
```

## Templates

**Modify:**

- `templates/login.html` — form already renders and POSTs to `/login`; confirm `{{ error }}` block is present (already in the template); no structural changes expected
- `templates/base.html` — update the navbar so it shows "Sign out" (linking to `/logout`) when a session exists, and "Sign in" / "Get started" when no session exists; use `session` in the Jinja2 context

## Files to change

- `app.py` — replace `GET /login` stub with a combined `GET`+`POST` handler; replace `GET /logout` stub with a session-clearing handler; add `session` to Flask imports; add `check_password_hash` to werkzeug imports; set `app.secret_key`
- `templates/base.html` — conditional navbar links based on `session.get('user_id')`

## Files to create

None.

## New dependencies

No new pip packages. `werkzeug` and Flask `session` are already available.

## Rules for implementation

- No SQLAlchemy or ORMs — use raw SQLite via `get_db()`
- Parameterised queries only — no f-strings or `%` formatting in SQL
- Passwords verified with `werkzeug.security.check_password_hash` — never compare plaintext
- Use CSS variables — never hardcode hex values in templates or stylesheets
- All templates extend `base.html`
- `app.secret_key` must be set before sessions will work — use a hardcoded dev string for now (e.g. `"spendly-dev-secret"`); note in a comment that this must be replaced with an env var before production
- On successful login store `session['user_id']` and `session['user_name']`
- On failed login (wrong email or wrong password) show the same generic error: `"Invalid email or password."` — do not distinguish between the two
- `/logout` must call `session.clear()` then redirect to `url_for('landing')`
- After successful login, redirect to `url_for('profile')` (still a stub — that's fine)

## Definition of done

- [ ] `GET /login` renders the login form
- [ ] Submitting correct credentials sets `session['user_id']` and redirects to `/profile`
- [ ] Submitting a wrong password re-renders the form with `"Invalid email or password."`
- [ ] Submitting an unregistered email re-renders the form with `"Invalid email or password."`
- [ ] Submitting with empty email or password re-renders the form with a validation error
- [ ] `GET /logout` clears the session and redirects to `/`
- [ ] The navbar shows "Sign out" when logged in and "Sign in" / "Get started" when logged out
- [ ] Running `pytest` produces no errors

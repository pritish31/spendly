import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import init_db, get_db

app = Flask(__name__)
app.secret_key = "spendly-dev-secret"  # replace with env var before production
init_db()


@app.template_filter("dateformat")
def dateformat(value, fmt="%d %b %Y"):
    return datetime.strptime(value, "%Y-%m-%d").strftime(fmt)


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("settings"))
    if request.method == "GET":
        return render_template("register.html")

    name     = request.form.get("name",     "").strip()
    email    = request.form.get("email",    "").strip()
    password = request.form.get("password", "").strip()

    if not name:
        return render_template("register.html", error="Name is required.")
    if not email:
        return render_template("register.html", error="Email is required.")
    if not password:
        return render_template("register.html", error="Password is required.")

    password_hash = generate_password_hash(password)

    try:
        db = get_db()
        with db:
            db.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, password_hash)
            )
    except sqlite3.IntegrityError:
        return render_template("register.html", error="An account with that email already exists.")

    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("settings"))
    if request.method == "GET":
        return render_template("login.html")

    email    = request.form.get("email",    "").strip()
    password = request.form.get("password", "").strip()

    if not email:
        return render_template("login.html", error="Email is required.")
    if not password:
        return render_template("login.html", error="Password is required.")

    db   = get_db()
    user = db.execute(
        "SELECT id, name, password_hash FROM users WHERE email = ?", (email,)
    ).fetchone()

    if user is None or not check_password_hash(user["password_hash"], password):
        return render_template("login.html", error="Invalid email or password.")

    session["user_id"]   = user["id"]
    session["user_name"] = user["name"]
    return redirect(url_for("profile"))


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/settings")
def settings():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    db   = get_db()
    user = db.execute(
        "SELECT name, email FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    success       = session.pop("profile_success", None)
    error         = session.pop("profile_error", None)
    error_section = session.pop("profile_error_section", None)

    return render_template("settings.html",
        user=user,
        success=success,
        error=error,
        error_section=error_section,
    )


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    db   = get_db()
    user = db.execute(
        "SELECT name, email, created_at FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    total_spent = db.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE user_id = ?",
        (session["user_id"],)
    ).fetchone()[0]

    tx_count = db.execute(
        "SELECT COUNT(*) FROM expenses WHERE user_id = ?",
        (session["user_id"],)
    ).fetchone()[0]

    recent = db.execute(
        "SELECT category, description, amount, date FROM expenses"
        " WHERE user_id = ? ORDER BY date DESC LIMIT 10",
        (session["user_id"],)
    ).fetchall()

    categories = db.execute(
        "SELECT category, SUM(amount) AS total FROM expenses"
        " WHERE user_id = ? GROUP BY category ORDER BY total DESC",
        (session["user_id"],)
    ).fetchall()

    top_category = categories[0]["category"] if categories else "—"

    created_dt   = datetime.strptime(user["created_at"][:10], "%Y-%m-%d")
    member_since = created_dt.strftime("%B %Y")
    account_days = (datetime.today().date() - created_dt.date()).days

    success       = session.pop("profile_success", None)
    error         = session.pop("profile_error", None)
    error_section = session.pop("profile_error_section", None)

    return render_template("profile.html",
        user=user,
        total_spent=total_spent,
        tx_count=tx_count,
        top_category=top_category,
        recent=recent,
        categories=categories,
        member_since=member_since,
        account_days=account_days,
        success=success,
        error=error,
        error_section=error_section,
    )


@app.route("/profile/update", methods=["POST"])
def profile_update():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    name  = request.form.get("name",  "").strip()
    email = request.form.get("email", "").strip()

    if not name or not email:
        session["profile_error"]         = "Name and email are required."
        session["profile_error_section"] = "update"
        return redirect(url_for("settings"))

    db = get_db()
    try:
        with db:
            db.execute(
                "UPDATE users SET name = ?, email = ? WHERE id = ?",
                (name, email, session["user_id"])
            )
        session["user_name"]      = name
        session["profile_success"] = "Profile updated successfully."
    except sqlite3.IntegrityError:
        session["profile_error"]         = "That email is already in use by another account."
        session["profile_error_section"] = "update"

    return redirect(url_for("settings"))


@app.route("/profile/password", methods=["POST"])
def profile_password():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    current = request.form.get("current_password", "")
    new_pw  = request.form.get("new_password",     "")
    confirm = request.form.get("confirm_password", "")

    db   = get_db()
    user = db.execute(
        "SELECT password_hash FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    if not check_password_hash(user["password_hash"], current):
        session["profile_error"]         = "Current password is incorrect."
        session["profile_error_section"] = "password"
        return redirect(url_for("settings"))

    if len(new_pw) < 6:
        session["profile_error"]         = "New password must be at least 6 characters."
        session["profile_error_section"] = "password"
        return redirect(url_for("settings"))

    if new_pw != confirm:
        session["profile_error"]         = "Passwords do not match."
        session["profile_error_section"] = "password"
        return redirect(url_for("settings"))

    with db:
        db.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (generate_password_hash(new_pw), session["user_id"])
        )

    session["profile_success"] = "Password updated successfully."
    return redirect(url_for("settings"))


@app.route("/profile/delete", methods=["POST"])
def profile_delete():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    db = get_db()
    with db:
        db.execute("DELETE FROM users WHERE id = ?", (session["user_id"],))

    session.clear()
    return redirect(url_for("landing"))


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)

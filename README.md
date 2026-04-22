# Spendly

A personal expense tracker built with Flask and SQLite. Track every dollar, know where it goes.

## Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLite (raw `sqlite3`, no ORM)
- **Frontend:** Jinja2 templates, Vanilla CSS, Vanilla JS
- **Auth:** Flask sessions + Werkzeug password hashing

## Getting Started

```bash
# Clone the repo
git clone <repo-url>
cd expense-tracker

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

The app runs at `http://localhost:5001`.

## Project Structure

```
expense-tracker/
├── app.py               # All routes
├── database/
│   └── db.py            # get_db(), init_db(), seed_db()
├── templates/
│   ├── base.html        # Shared layout (navbar, footer)
│   ├── landing.html     # Home page
│   ├── login.html       # Sign in form
│   ├── register.html    # Sign up form
│   ├── profile.html     # Dashboard
│   ├── terms.html       # Terms and Conditions
│   └── privacy.html     # Privacy Policy
├── static/
│   ├── css/style.css    # Single stylesheet with CSS variables
│   └── js/main.js       # Vanilla JS
├── requirements.txt
└── CLAUDE.md
```

## Features

- User registration and login
- Session-based authentication
- Expense dashboard with spending stats
- Spending breakdown by category

## Running Tests

```bash
source venv/bin/activate
pytest
```

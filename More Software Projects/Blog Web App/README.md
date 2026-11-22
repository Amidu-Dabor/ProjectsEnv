# Blog Web App (Flask)

A full-stack blog. Anyone can read posts, registered users can comment, and the site owner (the admin) writes, edits and deletes posts.

## Features

- **Accounts:** register, log in and log out (Flask-Login), with passwords hashed using Werkzeug.
- **Admin-only posting:** an `@admin_only` decorator restricts creating, editing and deleting posts to the first user (ID 1).
- **Rich-text posts** written with CKEditor.
- **Comments** on each post, linked to their authors.
- **Contact form** that emails the message to the site owner through Gmail's SMTP server.
- **Database:** SQLite through SQLAlchemy, with related users, posts and comments. Tables are created automatically on first run.

## Routes

`/` home · `/post/<id>` read and comment · `/new-post`, `/edit-post/<id>`, `/delete-post/<id>` (admin) · `/register` · `/login` · `/logout` · `/about` · `/contact`

## Run locally

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export FLASK_SECRET_KEY="any-long-random-string"
export RECIPIENT_EMAIL="you@example.com"          # for the contact form
export EMAIL_APP_PASSWORD="your-gmail-app-password"
python main.py
```

Open http://127.0.0.1:5000. The first account you register becomes the admin.

## Tech

Python · Flask · Flask-Login · Flask-SQLAlchemy · Flask-WTF · Flask-CKEditor · Flask-Bootstrap · SQLite · HTML/CSS

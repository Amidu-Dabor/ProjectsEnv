# USIU-Support: Student Help Desk (Django)

A help-desk web app for USIU-Africa. Students and staff raise support requests (tickets), discuss them in comments, and staff track activity on dashboards.

## Features

- **Separate sign-up and login for students and staff,** using a custom user model with departments, plus password reset by email.
- **Tickets:** create, view, update and delete support requests, organised by subject and department.
- **Comments:** discussion on each ticket, with edit and delete.
- **User profiles:** each user's tickets and activity.
- **Activity feed** of recent requests.
- **Dashboards:** a ticket dashboard and a pivot-table analytics view (WebDataRocks) fed by a data endpoint.
- **Admin panel:** the Django admin, with a custom theme.

## Project structure

| Path | Purpose |
|---|---|
| `QHelpDesk/` | Django project settings and URLs |
| `helpdesk/` | The app: models (`CustomUser`, `Department`, `Ticket`, `Subject`, `Comment`), views, forms, templates and migrations |
| `helpdesk/api/` | A Django REST Framework API (not switched on in `urls.py`) |
| `templates/`, `static/` | Shared templates, CSS, JavaScript and icons |
| `Data Analytics/` | A separate analysis of Stack Overflow question counts by programming language over time (`QueryResults.csv`) |

## Run locally

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export DJANGO_SECRET_KEY="any-long-random-string"
export EMAIL_HOST_PASSWORD="your-email-app-password"   # only needed for password-reset emails
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000.

The database is created by `migrate` and is not committed. `echosystem.config.json` runs the app with PM2 on port 8082.

## Tech

Python · Django · SQLite · Django REST Framework · django-ckeditor · Bootstrap · jQuery DataTables · WebDataRocks

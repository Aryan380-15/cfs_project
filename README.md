# Anonymous Teacher Feedback & College Improvement System
**Maharana Pratap Polytechnic**

Django-based platform for anonymous teacher feedback and a public
"You Said → We Did" college suggestion board.

> **Build status:** Phase 1 of 3 — project structure, database models,
> role-based authentication, and dashboard shells are complete.
> Feedback forms, public teacher profiles, suggestion board UI,
> analytics, and PDF/Excel export are being added in the next phases.

## Tech Stack
- Backend: Django 4.2+
- Database: MySQL
- Frontend: Bootstrap 5 + Chart.js
- Auth: Django's built-in auth with a custom `role` field (admin/teacher/student)

## Anonymity Design
Feedback anonymity isn't just "hide the name in the UI" — it's enforced at the
database level:
- `FeedbackSubmissionTracker` links Student ↔ Teacher only to stop duplicate
  submissions and check eligibility. It has no link to actual answers.
- `FeedbackResponse` / `FeedbackReview` (the actual ratings/comments) have
  **no foreign key to Student at all**. There is no query, join, or admin
  view anywhere in the codebase that connects a submission's tracker record
  to its content.
- `CollegeSuggestion` has no student reference whatsoever.

## Local Setup

### 1. Clone & create a virtual environment
```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```
> On Windows, if `mysqlclient` fails to build, use:
> `pip install mysqlclient --only-binary :all:` or install via
> `pip install pymysql` and add `import pymysql; pymysql.install_as_MySQLdb()`
> to `config/__init__.py` as a fallback.

### 3. Configure environment variables
```bash
cp .env.example .env
# then edit .env with your MySQL credentials and a real secret key
```

### 4. Set up MySQL
```sql
CREATE DATABASE cfs_db CHARACTER SET utf8mb4;
```

### 5. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a superuser (Admin)
```bash
python manage.py createsuperuser
```
After creating, set that user's `role` field to `admin` via
`/django-admin/` (Django's built-in admin, separate from the app's own
Admin dashboard at `/`).

### 7. Run the development server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/accounts/login/`

## Project Structure
```
cfs_project/
├── config/            # settings, root urls, wsgi/asgi
├── apps/
│   ├── accounts/       # custom User model + login/logout
│   ├── core/           # Department, Subject, Session, Notification, dashboards
│   ├── teachers/       # Teacher profile
│   ├── students/       # Student profile
│   ├── feedback/       # Questions, anonymous responses, submission tracker
│   └── suggestions/    # Anonymous College Suggestion Board
├── templates/          # base.html + per-app templates
├── static/css/theme.css
├── media/               # uploaded photos
├── requirements.txt
└── .env.example
```

## Roadmap (next build phases)
- **Phase 2:** Feedback submission flow (notice popup → dynamic 1–10 rating
  form → thank-you), public teacher profile with Chart.js graphs, student
  "my feedback" view.
- **Phase 3:** Suggestion board UI (submit, upvote, filter by category),
  "You Said → We Did" public timeline, admin status management.
- **Phase 4:** Analytics dashboards, CSV/Excel student import, PDF/Excel
  report export, notifications, search & pagination, abusive-language
  moderation on review submission.

## Screenshots
_(placeholders — add screenshots here once UI is finalized)_
- Login screen
- Admin dashboard
- Teacher public profile
- Suggestion board

## Future Improvements
- Email/SMS notifications for feedback deadlines
- Sentiment analysis on anonymous reviews
- Multi-language support

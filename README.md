# Project Tracker

A Django-based project tracker application for managing personal and corporate projects with next actions.

## Features

- Add, edit, and delete projects
- Track project types (corporate/personal)
- Set due dates (required for corporate projects)
- Define next actions for each project
- Automatic status calculation (on track, at risk, overdue, ongoing)
- Visual indicators for project types and status
- Statistics display

## Installation

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # Linux/Mac
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. Create a superuser (optional, for admin access):
   ```bash
   python manage.py createsuperuser
   ```

5. Run the development server:
   ```bash
   python manage.py runserver
   ```

6. Open your browser and navigate to `http://127.0.0.1:8000/`

## Usage

- Click "+ add project" to create a new project
- Corporate projects require a due date
- Personal projects can have optional due dates
- Click the edit (✎) button to modify a project
- Click the remove (✕) button to delete a project
- Projects are automatically sorted by status priority (overdue → at risk → on track → ongoing)

## Admin Interface

Access the Django admin interface at `http://127.0.0.1:8000/admin/` to manage projects through the admin panel.

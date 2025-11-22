# Campus Event Management System

A complete Event Management System built with Flask, SQLAlchemy, and Bootstrap that allows clubs to create events, students to register for events, and admins to manage the system.

## Features

### 🔐 Three Login Types
- **Club Login**: Create events, manage registrations, accept/reject students
- **Student Login**: View events, register for activities, check registration status
- **Admin Login**: Manage clubs, view all events and registrations

### 🎯 Core Functionality
- Event creation and management by clubs
- Student registration system with status tracking
- Admin dashboard for system oversight
- Session-based authentication
- Responsive Bootstrap UI

## Tech Stack

- **Backend**: Python 3.7+, Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML5, Bootstrap 5, Jinja2 templates
- **Authentication**: Flask sessions, password hashing

## Project Structure

```
Event/
├── app.py                 # Main Flask application
├── models.py              # SQLAlchemy models
├── init_db.py            # Database initialization script
├── database.db           # SQLite database (auto-created)
├── static/               # Static files (CSS, JS, images)
├── templates/            # HTML templates
│   ├── base.html        # Base template with navigation
│   ├── index.html       # Home page
│   ├── club_login.html  # Club login page
│   ├── student_login.html # Student login page
│   ├── student_register.html # Student registration
│   ├── admin_login.html # Admin login page
│   ├── club_dashboard.html # Club dashboard
│   ├── student_dashboard.html # Student dashboard
│   ├── admin_dashboard.html # Admin dashboard
│   ├── create_event.html # Create event form
│   ├── register_event.html # Event registration form
│   └── add_club.html    # Add new club form
└── README.md            # This file
```

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Step 1: Install Dependencies

```bash
pip install flask flask-sqlalchemy werkzeug
```

### Step 2: Initialize the Database

```bash
python init_db.py
```

This will:
- Create the SQLite database
- Add 5 default clubs (Club A-E with password "1234")
- Create sample students and events for testing

### Step 3: Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## Default Credentials

### Club Login
- **Club Name**: Club A, Club B, Club C, Club D, Club E
- **Password**: 1234

### Student Login (Sample Accounts)
- **Register Number**: REG001, REG002, REG003
- **Password**: password123

### Admin Login
- **Username**: admin
- **Password**: admin123

## Usage Guide

### For Clubs
1. Login with club credentials
2. Create events with name, description, and credits
3. View student registrations for your events
4. Accept or reject registration requests

### For Students
1. Register a new account or login
2. Browse all available events from different clubs
3. Register for events of interest
4. Track registration status (Pending/Accepted/Rejected)

### For Admins
1. Login with admin credentials
2. View all clubs, events, and registrations
3. Add new clubs to the system
4. Delete existing clubs (and their events)

## Database Schema

### Tables:
- **clubs**: Club information (id, club_name, password)
- **students**: Student details (id, name, reg_no, email, password)
- **events**: Event details (id, club_id, event_name, description, credits, created_at)
- **registrations**: Registration tracking (id, student_id, event_id, status, registered_at)

### Relationships:
- Clubs → Events (One-to-Many)
- Students → Registrations (One-to-Many)
- Events → Registrations (One-to-Many)

## Security Features

- Password hashing for student accounts
- Session-based authentication
- Input validation
- SQL injection prevention via SQLAlchemy ORM
- CSRF protection (Flask's built-in security)

## Development

### Adding New Features
1. Modify models.py for database changes
2. Update routes in app.py
3. Create/modify templates in templates/
4. Run `python init_db.py` if database schema changes

### Customization
- Update `SECRET_KEY` in app.py for production
- Modify database URI for MySQL/PostgreSQL
- Customize Bootstrap theme in templates/base.html

## Troubleshooting

### Common Issues:
1. **Database Error**: Run `python init_db.py` to reinitialize
2. **Import Error**: Ensure all dependencies are installed
3. **Permission Error**: Check file permissions for database.db

### Port Already in Use:
```bash
# Kill the process or use different port
python app.py
```

## Production Deployment

For production deployment:
1. Set `app.debug = False` in app.py
2. Use a production WSGI server (Gunicorn, uWSGI)
3. Configure proper database (MySQL/PostgreSQL)
4. Set up environment variables for sensitive data
5. Use HTTPS and proper security headers

## License

This project is for educational purposes. Feel free to modify and use according to your needs.

## Support

For issues or questions, please check the code comments and documentation provided.

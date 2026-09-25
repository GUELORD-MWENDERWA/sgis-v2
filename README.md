# SGIS: School Management Information System

A REST API for school administration built with Django REST Framework. It manages users and roles, school years, classes, students and attendance, with three ways of recording attendance: QR codes scanned from a mobile or web client, RFID cards read by ESP32 terminals, and manual entry by staff.

## Features

- **Accounts**: custom user model with student, parent, teacher and administrator roles; JWT authentication with refresh tokens; profile and photo management
- **Academic structure**: school years, classrooms with assigned teachers, student profiles and enrolments
- **QR attendance**: a personal QR code generated per user; scans are validated server-side and recorded as check-in or check-out depending on the current state
- **RFID attendance**: card inventory, card-to-user assignment, registration of ESP32 reader modules identified by a module token
- **Attendance sessions**: per-class sessions, attendance reports and absence notifications
- **Role-based permissions** enforced on every endpoint
- **Environment-specific settings** (`dev`, `prod`) and deployment descriptors for Render

## Architecture

The project is split into independent Django apps:

| App | Responsibility |
| --- | --- |
| `accounts` | Users, roles, authentication, profiles |
| `schoolyear` | School years |
| `classes` | Classrooms and teachers |
| `students` | Student profiles and enrolments |
| `qrcodes` | QR code generation and validation |
| `rfid` | RFID cards and ESP32 reader modules |
| `attendance` | Sessions, records, reports, notifications |

```
 Mobile / web client ── QR scan ──┐
                                  ├──> Django REST API ──> PostgreSQL
 ESP32 + RC522 ── card UID + ─────┘        (JWT)
                  module token
```

## API overview

All endpoints except login require `Authorization: Bearer <access_token>`.

| Area | Endpoints |
| --- | --- |
| Authentication | `POST /api/auth/login/`, `POST /api/auth/refresh/`, `GET /api/auth/me/`, `GET /api/auth/me/full/` |
| Profile | `PUT /api/auth/profile/update/`, `POST /api/auth/change-password/`, `POST /api/auth/upload/photo/` |
| User management | `POST /api/auth/create/student/`, `/create/parent/`, `/create/teacher/`, `GET /api/auth/list/` |
| School years | `/api/schoolyears/` (CRUD) |
| Classes | `/api/classes/` (CRUD) |
| Students | `/api/students/` (CRUD) |
| QR codes | `/api/qrcode/qrcodes/`, `GET /api/qrcode/my/`, `POST /api/qrcode/validate/` |
| RFID | `/api/rfid/cards/create/`, `/cards/available/`, `/cards/assign/`, `/modules/`, `/modules/create/`, `/modules/check/` |
| Attendance | `/api/attendance/attendance/`, `/api/attendance/session/`, `POST /api/attendance/scan/`, `POST /api/attendance/rfid/`, `GET /api/attendance/report/`, `POST /api/attendance/notify/` |

Module-level documentation is in [`docs/`](docs), and runnable request collections for every app are in [`test_api/`](test_api) (VS Code REST Client format).

## Attendance flows

**QR code**: the user presents their QR code, the client posts the scanned token to `/api/attendance/scan/`, and the server records a check-in or check-out.

**RFID**: an ESP32 terminal reads a card and posts the `rfid_uid` together with its `module_token` to `/api/attendance/rfid/`. Terminals can verify their registration with `/api/rfid/modules/check/`.

**Manual**: a teacher or administrator creates a record through `/api/attendance/attendance/` with `entry_method: "MANUAL"`.

## Getting started

Requirements: Python 3.10 or later.

```bash
git clone https://github.com/GUELORD-MWENDERWA/sgis-v2.git
cd sgis-v2
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
# create a .env file with the variables listed below
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

`manage.py` uses `school_management.settings.dev` by default. Set `DJANGO_SETTINGS_MODULE=school_management.settings.prod` in production.

### Environment variables

| Variable | Description |
| --- | --- |
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` in development |
| `DATABASE_URL` | Database connection string (SQLite in development, PostgreSQL in production) |

## Deployment

`render.yaml` provisions a web service and a PostgreSQL database on Render; `Procfile` starts Gunicorn for Heroku-style platforms. Static files are served with WhiteNoise.

## Tech stack

Python, Django 5.2, Django REST Framework, Simple JWT, django-cors-headers, qrcode, Pillow, PostgreSQL, Gunicorn, WhiteNoise.

## Roadmap

- ESP32 reader firmware published as a companion repository
- Web and mobile front ends
- Automated test suite and CI

## License

No license has been specified yet. Contact the author before reusing this code.

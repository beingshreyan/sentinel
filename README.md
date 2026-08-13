# Sentinel

Sentinel is a lightweight web-based telemetry and tracking prototype built with HTML, CSS, JavaScript, FastAPI, and Google Sheets.

The current version is an MVP designed to experiment with browser-based information collection, GPS permission-based location collection, centralized storage, and a private administrator dashboard.

> **Important:** Sentinel should only be used with people, devices, and environments where the relevant data collection is authorized and clearly disclosed.

---

## Features

### User Interface

- E-commerce-style computer hardware interface
- Computer component listings
- Required customer information form
- Name collection
- Email collection
- Phone number collection
- Browser-based GPS permission
- GPS latitude
- GPS longitude
- GPS accuracy
- Browser information
- Operating-system information exposed by the browser
- Device category
- Server-observed IP address
- Timestamp

### Admin Interface

- Single administrator account
- Username/password authentication
- Salted password hashing with Argon2
- Secure authentication session
- Private admin dashboard
- Collected record viewer
- GPS coordinates
- "Show in Maps" functionality
- Refresh records
- Logout

### Storage

The current MVP uses Google Sheets as its database.

SQL storage can be introduced in a later version.

---

# Technology Stack

## Frontend

- HTML5
- CSS3
- Vanilla JavaScript

## Backend

- Python
- FastAPI
- Uvicorn

## Database

- Google Sheets
- Google Sheets API
- gspread

## Authentication

- Argon2id
- Signed session cookie

## Hosting

The intended deployment architecture is:

- Frontend: Vercel
- Backend: Render or another FastAPI-compatible cloud service
- Database: Google Sheets

---

# Project Structure

```text
sentinel/
│
├── frontend/
│   ├── index.html
│   ├── user.html
│   ├── admin.html
│   ├── dashboard.html
│   │
│   ├── css/
│   │   ├── style.css
│   │   ├── user.css
│   │   └── admin.css
│   │
│   └── js/
│       ├── user.js
│       ├── admin.js
│       └── dashboard.js
│
├── backend/
│   ├── main.py
│   ├── auth.py
│   ├── sheets.py
│   ├── requirements.txt
│   └── google-service-account.json
│
├── .env
├── .env.example
├── .gitignore
└── README.md
```

`google-service-account.json` and `.env` must never be committed to the public repository.

---

# Local Development

## 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd sentinel
```

## 2. Create a virtual environment

```bash
python3 -m venv .venv
```

Activate it:

### macOS / Linux

```bash
source .venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r backend/requirements.txt
```

---

# Google Sheets Configuration

Create a Google Cloud project and enable:

- Google Sheets API

Create a service account and download its JSON credentials.

Place the credentials inside the backend during local development:

```text
backend/google-service-account.json
```

Share the Sentinel Google Sheet with the service-account email address and give it Editor access.

The first row of the sheet should contain the headers used by Sentinel.

Example:

```text
ID
Timestamp
Name
Email
Phone
IPv4
IPv6
Network
Browser
OS
Device
Latitude
Longitude
Accuracy
```

---

# Environment Variables

Create `.env` in the project root.

Example:

```env
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD_HASH=your_argon2_password_hash

GOOGLE_SHEET_ID=your_google_sheet_id
GOOGLE_SERVICE_ACCOUNT_FILE=backend/google-service-account.json

SESSION_SECRET=your_random_session_secret

ENVIRONMENT=development
COOKIE_SECURE=false
CORS_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
```

Do not commit `.env` to GitHub.

For the public repository, use `.env.example` with empty values:

```env
ADMIN_USERNAME=
ADMIN_PASSWORD_HASH=

GOOGLE_SHEET_ID=
GOOGLE_SERVICE_ACCOUNT_FILE=

SESSION_SECRET=

ENVIRONMENT=
COOKIE_SECURE=
CORS_ORIGINS=
```

---

# Generate the Admin Password Hash

Sentinel does not store the administrator password in plaintext.

Generate an Argon2 password hash:

```bash
python -c "from argon2 import PasswordHasher; print(PasswordHasher().hash(input('Enter admin password: ')))"
```

Copy the resulting hash into:

```env
ADMIN_PASSWORD_HASH=
```

Generate a session secret with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Copy the result into:

```env
SESSION_SECRET=
```

---

# Run the Backend

From the project root:

```bash
uvicorn backend.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/api/health
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

---

# Run the Frontend

Do not open the HTML files directly with `file://`.

From the project root:

```bash
python3 -m http.server 5500 --directory frontend
```

The frontend will be available at:

```text
http://localhost:5500
```

User interface:

```text
http://localhost:5500/user.html
```

Admin interface:

```text
http://localhost:5500/admin.html
```

---

# Application Flow

## User

```text
/user
   ↓
Customer information form
   ↓
Location permission
   ↓
JavaScript
   ↓
POST /api/collect
   ↓
FastAPI
   ↓
Google Sheets
   ↓
Store interface becomes available
```

## Administrator

```text
/admin.html
   ↓
Username + Password
   ↓
POST /api/admin/login
   ↓
Authenticated session
   ↓
dashboard.html
   ↓
GET /api/admin/data
   ↓
Google Sheets
   ↓
Records displayed
```

---

# API Endpoints

## Root

```http
GET /
```

Returns the Sentinel API status.

---

## Health

```http
GET /api/health
```

Checks whether the backend is running.

---

## Collect Data

```http
POST /api/collect
```

Receives the information submitted by the user interface and stores the record in Google Sheets.

Example request:

```json
{
  "name": "Test User",
  "email": "test@example.com",
  "phone": "9999999999",
  "latitude": 22.5726,
  "longitude": 88.3639,
  "accuracy": 10,
  "browser": "Safari",
  "os": "macOS",
  "device": "Desktop"
}
```

---

## Admin Login

```http
POST /api/admin/login
```

Authenticates the single administrator.

---

## Admin Logout

```http
POST /api/admin/logout
```

Ends the current administrator session.

---

## Admin Authentication Check

```http
GET /api/admin/check
```

Checks whether the current session is authenticated.

---

## Admin Data

```http
GET /api/admin/data
```

Returns stored records.

This endpoint requires an authenticated administrator session.

---

# Location

Sentinel uses the browser's Geolocation API.

The browser requests location permission from the user.

When permission is granted, Sentinel can receive:

- Latitude
- Longitude
- Accuracy

The location is then submitted to FastAPI.

The administrator dashboard provides a **Show in Maps** option that opens the coordinates in an external mapping service.

---

# Security

The current MVP includes:

- HTTPS in production
- Argon2 password hashing
- Salted password hashing
- HTTP-only authentication cookies
- Secure cookies in production
- SameSite cookie protection
- Environment-based secrets
- Server-side Google credentials
- Backend-side authentication checks
- Basic request validation

The following files must remain private:

```text
.env
backend/google-service-account.json
```

---

# Open Source

Sentinel can be distributed as an open-source project.

Anyone cloning the repository should create their own:

- Google Cloud project
- Google Sheet
- Service account
- Administrator credentials
- Environment configuration

The source code can be shared without sharing private credentials or collected data.

---

# Deployment

Recommended architecture:

```text
GitHub
   │
   ├── Frontend → Vercel
   │
   └── Backend → FastAPI hosting service
                       │
                       ↓
                  Google Sheets
```

For production:

```env
COOKIE_SECURE=true
CORS_ORIGINS=https://your-frontend-domain
```

The production frontend must use the deployed FastAPI URL instead of:

```javascript
http://127.0.0.1:8000
```

---

# Current MVP Scope

The current version intentionally stays lightweight.

It uses:

- HTML
- CSS
- JavaScript
- FastAPI
- Google Sheets
- One administrator

A future version may replace Google Sheets with SQL storage and introduce additional capabilities.

---

# Disclaimer

Sentinel is a cybersecurity research and development project.

Use it only in environments where you have appropriate authorization to collect and process the information involved. Do not use it to secretly collect private information, bypass browser or operating-system permissions, or access accounts, devices, or data without authorization.

---

## Author

**Shreyan**

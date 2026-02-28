# Smart Attendance System

## Overview

Smart Attendance System is a full-stack web application developed to digitize and streamline attendance management in educational institutions. The system supports multiple roles including Admin, HOD, Teacher, and Student, each with dedicated dashboards and functionalities.

The project demonstrates backend API development, role-based UI design, authentication handling, and structured frontend architecture.

---

## Features

### Authentication & Roles
- Student login and registration
- Teacher login and registration
- Admin login
- HOD login
- Role selection system

### Attendance Management
- Mark and view attendance
- New attendance entry
- Student dashboard attendance tracking
- Teacher attendance handling

### Academic Management
- Assignment management
- Notes upload/view
- Results display
- Certificates section
- Semester view
- Announcements

---

## Technology Stack

### Backend
- Python
- FastAPI
- Uvicorn

### Frontend
- HTML
- CSS
- JavaScript

### Server / Runtime
- Node.js (package.json, index.js)

### Version Control
- Git & GitHub

---

## Project Structure
smart-attendance-system/
│
├── major/
│ ├── backend/
│ │ ├── main.py
│ │ └── pycache/
│ │
│ ├── frontend/
│ │ ├── admin_login.html
│ │ ├── student_login.html
│ │ ├── teacher_login.html
│ │ ├── attendance.html
│ │ ├── dashboard files
│ │ ├── CSS files
│ │ └── image assets
│ │
│ ├── index.js
│ ├── package.json
│ ├── package-lock.json
│ ├── requirements.txt
│ └── .gitignore
│
└── README.md

---

## Installation & Setup

### 1. Clone Repository


git clone https://github.com/moulyajagarlamudi/smart-attendance-system.git

cd smart-attendance-system/major

---

### 2. Backend Setup (FastAPI)

Create virtual environment:

python -m venv venv

Activate:

Windows:

venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Run backend server:

uvicorn backend.main:app --reload

---

### 3. Frontend Setup

Open frontend HTML files directly in browser  
OR  
Run Node server:

npm install
node index.js

---

## Architecture Notes

- Role-based frontend separation
- Dedicated dashboards per user type
- Backend API handling attendance logic
- Modular folder separation (backend/frontend)
- Scalable structure for adding new modules

---

## Improvements Planned

- JWT-based authentication
- Database normalization
- Role-based access control at backend level
- Deployment using Docker
- Production hosting

---

## Author

GitHub: https://github.com/moulyajagarlamudi

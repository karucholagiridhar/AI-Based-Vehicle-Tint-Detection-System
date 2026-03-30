# AI-Based Vehicle Tint Detection System

Web application for detecting tinted vehicle windows from images, videos, and webcam captures using a Roboflow model and OpenCV-based processing.

## Overview

This project provides:

- User authentication and profile management
- AI-powered tint detection workflows
- Result history with annotated output images
- Dashboard analytics (tests, detections, confidence, trends)
- Deployment-ready Flask structure

## Key Features

- Image tint detection via upload
- Video tint detection by frame extraction and batch inference
- Webcam capture and detection
- Detection classes: tinted and clear
- Automatic metrics tracking per user
- Responsive UI with charts and status feedback

## Tech Stack

- Backend: Flask, Flask-SQLAlchemy, SQLAlchemy
- AI/Computer Vision: Roboflow Inference SDK, OpenCV, NumPy, Pillow
- Frontend: Jinja templates, JavaScript, Chart.js
- Database: SQLite (default), PostgreSQL/MySQL supported through DATABASE_URL

## Project Structure

```text
flask_app/
    app/
        __init__.py
        auth_routes.py
        config.py
        inference.py
        main_routes.py
        models.py
        profile_api.py
        static/
            css/
            js/
            uploads/
        templates/
            auth/
            main/
    instance/
        car_tint_detection.db
    DEPLOYMENT.md
    GETTING_STARTED.md
    HEROKU_DEPLOYMENT.md
    requirements.txt
    run.py
```

## Prerequisites

- Python 3.8+
- pip
- Virtual environment

## Quick Start (Windows PowerShell)

1. Go to the repository root:

```powershell
cd C:\projects\CarTitntDetection
```

2. Activate virtual environment:

```powershell
& .\.venv\Scripts\Activate.ps1
```

3. Go to the Flask app directory:

```powershell
cd .\CarTintDetection\flask_app
```

4. Install dependencies:

```powershell
pip install -r requirements.txt
```

5. Run the app:

```powershell
python run.py
```

6. Open in browser:

```text
http://127.0.0.1:5000
```

## Environment Variables

Create a .env file in flask_app using .env.example as reference.

Common keys:

- FLASK_ENV=development or production
- SECRET_KEY=your_secure_key
- DATABASE_URL=sqlite:///car_tint_detection.db (or postgres/mysql URL)
- ROBOFLOW_API_URL=https://serverless.roboflow.com
- ROBOFLOW_API_KEY=your_api_key
- MODEL_ID=your_model_id
- MAX_CONTENT_LENGTH=16777216 (example for 16MB)

## Core Routes

Authentication:

- GET/POST /auth/register
- GET/POST /auth/login
- GET /auth/logout

Main pages:

- GET /
- GET /dashboard
- GET /test
- GET /test/image
- GET /test/video
- GET /test/webcam
- GET /results
- GET /results/<result_id>
- GET /stats
- GET /logs

Detection endpoints:

- POST /test/image
- POST /test/video
- POST /test/webcam

Profile API:

- GET /api/profile/get
- POST /api/profile/update
- POST /api/profile/change-password

## Data Model Summary

- User: account and profile fields
- TestResult: test type, file paths, counts, confidence, processing time, raw predictions
- PerformanceLog: per-user aggregate stats

## Deployment

Deployment guides are included:

- DEPLOYMENT.md
- HEROKU_DEPLOYMENT.md

Also included:

- Procfile
- gunicorn.conf.py
- runtime.txt

## Troubleshooting

Port already in use (Windows):

```powershell
netstat -ano | findstr :5000
taskkill /F /PID <PID>
```

Reinstall dependencies:

```powershell
pip install -r requirements.txt
```

Reset local SQLite database (development only):

```powershell
Remove-Item .\instance\car_tint_detection.db
python run.py
```

## Notes

- Upload outputs are saved under app/static/uploads.
- Keep API keys and secrets only in environment variables for production.
- For production hardening, configure HTTPS, secure cookies, CSRF, and rate limiting.

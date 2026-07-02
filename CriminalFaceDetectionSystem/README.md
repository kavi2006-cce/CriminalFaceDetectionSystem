# Criminal Face Detection System (CFCS)

This repository contains a full-stack Criminal Face Detection System:

- `backend/criminalfacedetection`: Spring Boot + JPA REST API
- `frontend`: static HTML/CSS/JS admin UI pages
- `python-ai`: OpenCV face detection microservice

## Quick start

### 1) Backend (Spring Boot)

1. Ensure MySQL is running and database `criminal_db` exists.
2. Update `backend/criminalfacedetection/src/main/resources/application.properties` with your MySQL credentials.
3. Run:
   - `cd backend/criminalfacedetection`
   - `mvn test` (or `mvn spring-boot:run`)
4. Access APIs on `http://localhost:8080/criminal`:
   - GET `/all`, POST `/add`, GET `/{id}`, PUT `/{id}`, DELETE `/{id}`, GET `/search?name=`

### 2) Frontend

1. Open `frontend/login.html` in a browser.
2. Login with `admin` / `admin123`.
3. Use Add Criminal, Criminal List, Detect Face.

### 3) Python face detection microservice

1. Create and activate virtual env:
   - `python -m venv venv`
   - `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/macOS)
2. Install requirements:
   - `pip install -r python-ai/requirements.txt`
3. Run server:
   - `python python-ai/face_detect.py`
4. In frontend, open `frontend/detect-face.html`; upload image and click Detect Face.

## Notes

- `frontend/detect-face.html` is connected to Python service at `http://localhost:5000/detect`.
- Backend includes CRUD endpoints for criminals.


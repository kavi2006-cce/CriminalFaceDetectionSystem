# CFCS v2.0 — Criminal Face Detection & Smart Surveillance System

> **AI-Powered Law Enforcement Intelligence Platform**  
> Real-time face recognition · Criminal database · Smart alerts · Analytics · AI assistant

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip

### Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Seed the database (creates admin + sample data)
python seed_db.py

# 3. Start the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# OR — Launch using Docker Compose:
docker-compose up --build

# OR — on Windows, just double-click:
run.bat
```

### Default Credentials & Roles
| Role | Username | Password |
|------|----------|----------|
| **Admin** | `admin` | `admin123` |
| **Police / Officer** | `police` | `admin123` |
| **Investigator** | `investigator` | `admin123` |
| **Operator** | `operator` | `admin123` |

Open: **http://localhost:8000** (Landing Page) | **http://localhost:8000/login** (Portal Auth)

---

## 📚 Technical Documentation
- 🏗 [System Architecture](file:///d:/CFCS/docs/ARCHITECTURE.md)
- 🗄 [Database ERD & Schema](file:///d:/CFCS/docs/DATABASE_ERD.md)
- 🔌 [REST API Reference](file:///d:/CFCS/docs/API_DOCUMENTATION.md)

---

## 📸 Platform Overview

CFCS is a full-stack AI surveillance intelligence platform featuring:

| Module | Description |
|--------|-------------|
| 🏠 Dashboard | Real-time stats, activity feed, camera grid |
| 📹 Live Surveillance | Webcam feed with real-time face scanning |
| 🗂 Criminal Database | Full CRUD, photo upload, CSV export |
| 🔍 Detection Logs | All face detection events with screenshots |
| 📊 Analytics | Chart.js graphs + Leaflet crime heatmap |
| 🚨 Alert Center | Active alerts, emergency mode, siren |
| 🤖 AI Assistant | Natural language query (ARIA) |
| ⚙️ Settings | Camera management, system config |

---

## 🏗 Architecture

```
d:\CFCS\
├── main.py              ← FastAPI app (all API routes + page routes)
├── models.py            ← SQLAlchemy models (Criminal, Camera, DetectionLog, AlertLog…)
├── schemas.py           ← Pydantic schemas
├── auth.py              ← JWT authentication
├── vision.py            ← Face detection + LBPH recognition + DeepFace (optional)
├── database.py          ← SQLite engine
├── seed_db.py           ← Demo data seeder
├── requirements.txt
├── run.bat              ← Windows one-click startup
│
├── templates/           ← Jinja2 HTML pages
│   ├── login.html       ← Split-panel auth page
│   ├── dashboard.html   ← Command center
│   ├── surveillance.html← Live webcam + face scan
│   ├── criminals.html   ← Criminal database (card + table view)
│   ├── detections.html  ← Detection log table
│   ├── analytics.html   ← Chart.js + Leaflet analytics
│   ├── alerts.html      ← Alert center + emergency mode
│   ├── settings.html    ← Camera config + system panel
│   └── chat.html        ← ARIA AI assistant
│
├── static/
│   ├── css/main.css     ← Shared glassmorphism design system
│   ├── js/auth.js       ← JWT token management
│   ├── js/api.js        ← API client + utilities
│   └── uploads/         ← Criminal photos, detection screenshots
│
├── dataset_criminals/   ← Grayscale face crops for LBPH training
├── trainer_criminals.yml← Trained LBPH model
└── haarcascade_frontalface_default.xml
```

---

## 🔌 API Reference

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/token` | Login → JWT token |

### Criminals
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/criminals` | List all (search, filter) |
| POST | `/api/criminals` | Create record + upload photo |
| GET | `/api/criminals/{id}` | Get single record |
| PUT | `/api/criminals/{id}` | Update record |
| DELETE | `/api/criminals/{id}` | Delete + retrain model |

### Detection & Recognition
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/recognize` | Match face → criminal DB |
| GET | `/api/detections` | Detection log |
| GET | `/api/alerts` | Alert log |
| PUT | `/api/alerts/{id}/resolve` | Resolve alert |
| POST | `/api/alerts/emergency` | Trigger emergency |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stats` | Dashboard stats |
| GET | `/api/analytics/trends?days=7` | Detection trend data |
| GET | `/api/analytics/threat-distribution` | Threat level counts |
| GET | `/api/analytics/camera-activity` | Per-camera detection count |
| GET | `/api/analytics/geo-data` | Criminal lat/lng data |

### AI Assistant
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Natural language query → JSON response |

### Cameras
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/cameras` | List cameras |
| POST | `/api/cameras` | Add camera |
| DELETE | `/api/cameras/{id}` | Remove camera |

---

## 🧠 AI Features

| Feature | Technology |
|---------|-----------|
| Face Detection | OpenCV Haar Cascade |
| Face Recognition | OpenCV LBPH |
| Age/Gender Estimation | DeepFace (optional) |
| Natural Language Queries | Keyword NLP (ARIA) |
| Crime Map | Leaflet.js |
| Trend Analysis | Chart.js |

### Using DeepFace (Optional)
```bash
pip install deepface tf-keras
```
Once installed, the system automatically uses it for age/gender estimation on each detected face. Face recognition still uses LBPH (faster, offline).

---

## 🎨 Design System

Built with a custom **glassmorphism dark theme**:
- CSS design tokens in `static/css/main.css`
- Inter font (body) + JetBrains Mono (data)
- Animated ambient backgrounds
- Threat-level color coding (Low → Green, Critical → Red pulse)
- Responsive grid layout

---

## 🔐 Security

- JWT tokens (1-day expiry)
- bcrypt password hashing
- All API endpoints require valid token
- Face photos stored locally (no cloud)
- SQLite database (offline capable)

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.9 + FastAPI |
| Database | SQLite + SQLAlchemy |
| Auth | JWT + bcrypt |
| Face AI | OpenCV 4.x + LBPH |
| Templates | Jinja2 |
| Frontend | HTML5 + Vanilla CSS/JS |
| Charts | Chart.js v4 |
| Maps | Leaflet.js |

---

## 🗺 Deployment

### Local (Development)
```bash
uvicorn main:app --reload --port 8000
```

### Production (Render / Railway)
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT --workers 2
```

### Vercel
The included `vercel.json` routes all requests to the FastAPI app via the `api/index.py` entry point.

---

*CFCS v2.0 — Built for law enforcement, smart cities, and institutional security.*

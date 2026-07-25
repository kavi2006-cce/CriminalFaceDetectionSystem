# System Architecture & Technical Design — CFCS v2.0

## 1. High-Level Architecture Overview

The **Criminal Face Detection & Intelligent Surveillance System (CFCS v2.0)** is an enterprise-grade AI law enforcement platform. It processes multi-camera RTSP surveillance streams, live webcam feeds, and uploaded media to perform real-time face detection, criminal database matching, threat assessment, automated alerting, and spatial-temporal analytics.

```
                  ┌─────────────────────────────────────────┐
                  │           Surveillance Inputs           │
                  │  (Webcam / RTSP CCTV / Photo Uploads)   │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │       Python FastAPI Engine & Vision    │
                  │  - OpenCV Haar Cascade / LBPH           │
                  │  - DeepFace Age & Gender Analysis       │
                  │  - Real-time Multi-Face Bounding Boxes   │
                  └────────────────────┬────────────────────┘
                                       │
                      ┌────────────────┴────────────────┐
                      ▼                                 ▼
         ┌───────────────────────────┐     ┌───────────────────────────┐
         │  SQLAlchemy Database Engine│     │  Interactive Web Frontend │
         │  - Criminal Profiles      │     │  - Glassmorphic Dashboard │
         │  - Detection Logs         │     │  - Live Video Stream      │
         │  - Alert Logs & Cameras   │     │  - Leaflet Heatmaps       │
         └───────────────────────────┘     │  - Chart.js Analytics     │
                                           └───────────────────────────┘
```

---

## 2. Core Subsystems

### A. Computer Vision & Face Recognition Pipeline
1. **Face Detection**: Fast multi-scale face extraction via OpenCV Haar Cascade classifier (`haarcascade_frontalface_default.xml`).
2. **Face Crop Preprocessing**: Grayscale conversion, spatial normalization, and quality validation.
3. **Face Recognition**: Local Binary Patterns Histograms (LBPH) recognizer (`trainer_criminals.yml`) trained on known criminal dataset crops for instant low-latency identification.
4. **Attribute Analysis (DeepFace)**: Secondary pipeline for age and gender estimation when deep neural networks are active.

### B. Backend REST API & Authentication
- **Framework**: FastAPI with Uvicorn ASGI server.
- **Security**: OAuth2 with JWT Bearer Token validation, passkey hashing via bcrypt.
- **Role-Based Access Control (RBAC)**: Admin, Police Officer, Investigator, and System Operator roles.

### C. Frontend Command Center
- **Design Language**: Dark Glassmorphism system built with CSS variables (`--bg-body: #050816`, neon cyan/blue/purple glows, red threat highlights).
- **Visualization**: Chart.js for detection trends & threat distribution; Leaflet.js for interactive geospatial crime maps.
- **AI Assistant**: ARIA (Artificial Intelligence Assistant) capable of parsing natural language police queries.

---

## 3. Deployment Architecture

- **Docker Containerization**: Multi-stage `Dockerfile` with OpenCV and FastAPI dependencies.
- **Orchestration**: `docker-compose.yml` for zero-configuration startup.
- **Persistence**: Persistent storage volume bindings forSQLite DB (`cfcs.db`) and static uploaded criminal evidence photos (`/static/uploads`).

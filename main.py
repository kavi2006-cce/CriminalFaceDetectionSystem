from fastapi import FastAPI, Depends, HTTPException, Request, status, Form, UploadFile, File, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse, HTMLResponse, Response
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from pathlib import Path
from typing import Optional, List
import os, shutil, datetime, json, re, csv, io

import models
import schemas
import auth
import vision
from database import engine, Base, get_db

# ── App Setup ─────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

Base.metadata.create_all(bind=engine)
app = FastAPI(title="CFCS — Criminal Face Detection System", version="2.0.0")

for d in ["uploads/staff", "uploads/criminals", "uploads/detections", "uploads/temp"]:
    os.makedirs(STATIC_DIR / d, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# ── Page Routes ───────────────────────────────────────────────────────────────

@app.get("/")
async def landing_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.get("/dashboard")
async def dashboard_page(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html")

@app.get("/surveillance")
async def surveillance_page(request: Request):
    return templates.TemplateResponse(request=request, name="surveillance.html")

@app.get("/criminals")
async def criminals_page(request: Request):
    return templates.TemplateResponse(request=request, name="criminals.html")

@app.get("/detections")
async def detections_page(request: Request):
    return templates.TemplateResponse(request=request, name="detections.html")

@app.get("/analytics")
async def analytics_page(request: Request):
    return templates.TemplateResponse(request=request, name="analytics.html")

@app.get("/alerts")
async def alerts_page(request: Request):
    return templates.TemplateResponse(request=request, name="alerts.html")

@app.get("/settings")
async def settings_page(request: Request):
    return templates.TemplateResponse(request=request, name="settings.html")

@app.get("/chat")
async def chat_page(request: Request):
    return templates.TemplateResponse(request=request, name="chat.html")

@app.get("/staff_page")
async def staff_page(request: Request):
    return templates.TemplateResponse(request=request, name="staff.html")

@app.get("/recognition_page")
async def recognition_page(request: Request):
    return templates.TemplateResponse(request=request, name="recognition.html")

@app.get("/health")
def health_check():
    return {"status": "online", "service": "CFCS v2.0", "timestamp": datetime.datetime.utcnow().isoformat()}


# ── Auth ──────────────────────────────────────────────────────────────────────

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    admin = db.query(models.Admin).filter(models.Admin.username == form_data.username).first()
    if not admin or not auth.verify_password(form_data.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": admin.username})
    return {"access_token": access_token, "token_type": "bearer"}


# ── Dashboard Stats ───────────────────────────────────────────────────────────

@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db), current_admin: models.Admin = Depends(auth.get_current_admin)):
    today = datetime.date.today()
    detections_today = db.query(models.DetectionLog).filter(
        func.date(models.DetectionLog.detected_at) == today
    ).count()
    unknown_today = db.query(models.DetectionLog).filter(
        func.date(models.DetectionLog.detected_at) == today,
        models.DetectionLog.is_unknown == True
    ).count()
    return {
        "total_criminals": db.query(models.Criminal).count(),
        "active_alerts": db.query(models.AlertLog).filter(models.AlertLog.is_resolved == False).count(),
        "cameras_online": db.query(models.Camera).filter(models.Camera.status == "Online").count(),
        "total_cameras": db.query(models.Camera).count(),
        "detections_today": detections_today,
        "high_threat_count": db.query(models.Criminal).filter(
            models.Criminal.threat_level.in_(["High", "Critical"])
        ).count(),
        "unknown_persons_today": unknown_today,
        "total_staff": db.query(models.AuthorizedStaff).count(),
    }


# ── Criminal CRUD ─────────────────────────────────────────────────────────────

@app.post("/api/criminals", status_code=201)
async def create_criminal(
    name: str = Form(...),
    alias: str = Form(default=""),
    age: int = Form(default=0),
    gender: str = Form(default="Unknown"),
    fir_number: str = Form(default=""),
    crime_history: str = Form(default=""),
    case_status: str = Form(default="Active"),
    threat_level: str = Form(default="Medium"),
    last_seen_location: str = Form(default=""),
    nationality: str = Form(default=""),
    notes: str = Form(default=""),
    photo: Optional[UploadFile] = File(default=None),
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(auth.get_current_admin)
):
    image_path = None
    if photo and photo.filename:
        ext = Path(photo.filename).suffix
        fname = f"{name.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
        dest = STATIC_DIR / "uploads" / "criminals" / fname
        with open(dest, "wb+") as f:
            shutil.copyfileobj(photo.file, f)
        image_path = f"/static/uploads/criminals/{fname}"

    criminal = models.Criminal(
        name=name, alias=alias or None, age=age or None, gender=gender,
        fir_number=fir_number or None, crime_history=crime_history or None,
        case_status=case_status, threat_level=threat_level,
        last_seen_location=last_seen_location or None,
        nationality=nationality or None, notes=notes or None,
        image_path=image_path
    )
    db.add(criminal)
    db.commit()
    db.refresh(criminal)

    # Process face for recognition if photo uploaded
    if image_path:
        full_path = str(STATIC_DIR / "uploads" / "criminals" / Path(image_path).name)
        vision.process_and_save_face(full_path, criminal.id, is_criminal=True)
        vision.train_criminal_recognizer()

    return {"msg": "Criminal record created", "id": criminal.id}


@app.get("/api/criminals")
def list_criminals(
    search: Optional[str] = Query(default=None),
    threat_level: Optional[str] = Query(default=None),
    case_status: Optional[str] = Query(default=None),
    limit: int = Query(default=100),
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(auth.get_current_admin)
):
    q = db.query(models.Criminal)
    if search:
        q = q.filter(
            models.Criminal.name.contains(search) |
            models.Criminal.fir_number.contains(search) |
            models.Criminal.alias.contains(search)
        )
    if threat_level:
        q = q.filter(models.Criminal.threat_level == threat_level)
    if case_status:
        q = q.filter(models.Criminal.case_status == case_status)
    return q.order_by(models.Criminal.created_at.desc()).limit(limit).all()


@app.get("/api/criminals/{criminal_id}")
def get_criminal(criminal_id: int, db: Session = Depends(get_db), current_admin: models.Admin = Depends(auth.get_current_admin)):
    c = db.query(models.Criminal).filter(models.Criminal.id == criminal_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Criminal not found")
    return c


@app.put("/api/criminals/{criminal_id}")
async def update_criminal(
    criminal_id: int,
    name: str = Form(...),
    alias: str = Form(default=""),
    age: int = Form(default=0),
    gender: str = Form(default="Unknown"),
    fir_number: str = Form(default=""),
    crime_history: str = Form(default=""),
    case_status: str = Form(default="Active"),
    threat_level: str = Form(default="Medium"),
    last_seen_location: str = Form(default=""),
    nationality: str = Form(default=""),
    notes: str = Form(default=""),
    photo: Optional[UploadFile] = File(default=None),
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(auth.get_current_admin)
):
    c = db.query(models.Criminal).filter(models.Criminal.id == criminal_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Criminal not found")

    c.name = name
    c.alias = alias or None
    c.age = age or None
    c.gender = gender
    c.fir_number = fir_number or None
    c.crime_history = crime_history or None
    c.case_status = case_status
    c.threat_level = threat_level
    c.last_seen_location = last_seen_location or None
    c.nationality = nationality or None
    c.notes = notes or None
    c.updated_at = datetime.datetime.utcnow()

    if photo and photo.filename:
        ext = Path(photo.filename).suffix
        fname = f"{name.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
        dest = STATIC_DIR / "uploads" / "criminals" / fname
        with open(dest, "wb+") as f:
            shutil.copyfileobj(photo.file, f)
        c.image_path = f"/static/uploads/criminals/{fname}"

    db.commit()
    return {"msg": "Updated"}


@app.delete("/api/criminals/{criminal_id}")
def delete_criminal(
    criminal_id: int,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(auth.get_current_admin)
):
    c = db.query(models.Criminal).filter(models.Criminal.id == criminal_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Criminal not found")
    db.delete(c)
    db.commit()
    dataset_path = BASE_DIR / "dataset_criminals" / f"{criminal_id}.jpg"
    if dataset_path.exists():
        dataset_path.unlink()
    vision.train_criminal_recognizer()
    return {"msg": "Deleted"}


# ── Detection / Recognition ───────────────────────────────────────────────────

@app.post("/api/recognize")
async def recognize_face_endpoint(
    photo: UploadFile = File(...),
    camera_id: Optional[int] = Form(default=None),
    camera_location: Optional[str] = Form(default="Manual Upload"),
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(auth.get_current_admin)
):
    try:
        temp_dir = STATIC_DIR / "uploads" / "temp"
        temp_path = temp_dir / f"tmp_{datetime.datetime.now().strftime('%H%M%S%f')}{Path(photo.filename).suffix}"
        with open(temp_path, "wb+") as f:
            shutil.copyfileobj(photo.file, f)

        result = vision.recognize_criminal_face(str(temp_path))

        # Save screenshot
        ss_fname = f"det_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S%f')}.jpg"
        ss_path = STATIC_DIR / "uploads" / "detections" / ss_fname
        shutil.copy(temp_path, ss_path)
        if temp_path.exists():
            temp_path.unlink()

        screenshot_rel = f"/static/uploads/detections/{ss_fname}"

        if result["match"]:
            criminal = db.query(models.Criminal).filter(models.Criminal.id == result["criminal_id"]).first()
            if criminal:
                # Update last seen
                criminal.last_seen_at = datetime.datetime.utcnow()
                criminal.last_seen_location = camera_location

                # Log detection
                log = models.DetectionLog(
                    criminal_id=criminal.id,
                    criminal_name=criminal.name,
                    camera_id=camera_id,
                    camera_location=camera_location,
                    confidence=result.get("confidence", 0),
                    threat_level=criminal.threat_level,
                    screenshot_path=screenshot_rel,
                    age_estimate=result.get("age"),
                    gender_estimate=result.get("gender"),
                    is_unknown=False
                )
                db.add(log)

                # Create alert
                alert = models.AlertLog(
                    criminal_id=criminal.id,
                    criminal_name=criminal.name,
                    alert_type="Detection",
                    severity=criminal.threat_level,
                    message=f"Criminal '{criminal.name}' (FIR: {criminal.fir_number}) detected at {camera_location} with {result.get('confidence', 0):.1f}% confidence.",
                    camera_location=camera_location
                )
                db.add(alert)
                db.commit()

                return {
                    "match": True,
                    "criminal": {
                        "id": criminal.id, "name": criminal.name, "alias": criminal.alias,
                        "fir_number": criminal.fir_number, "threat_level": criminal.threat_level,
                        "crime_history": criminal.crime_history, "case_status": criminal.case_status,
                        "image_path": criminal.image_path
                    },
                    "confidence": result.get("confidence", 0),
                    "age_estimate": result.get("age"),
                    "gender_estimate": result.get("gender"),
                    "screenshot": screenshot_rel,
                    "alert_id": alert.id
                }

        # Unknown person
        log = models.DetectionLog(
            camera_id=camera_id,
            camera_location=camera_location,
            confidence=0,
            threat_level="Unknown",
            screenshot_path=screenshot_rel,
            age_estimate=result.get("age"),
            gender_estimate=result.get("gender"),
            is_unknown=True
        )
        db.add(log)
        db.commit()

        return {
            "match": False,
            "message": "No criminal match found",
            "age_estimate": result.get("age"),
            "gender_estimate": result.get("gender"),
            "screenshot": screenshot_rel
        }

    except Exception as e:
        print(f"Recognition error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Detection Logs ────────────────────────────────────────────────────────────

@app.get("/api/detections")
def get_detections(
    limit: int = Query(default=50),
    criminal_id: Optional[int] = Query(default=None),
    threat_level: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(auth.get_current_admin)
):
    q = db.query(models.DetectionLog)
    if criminal_id:
        q = q.filter(models.DetectionLog.criminal_id == criminal_id)
    if threat_level:
        q = q.filter(models.DetectionLog.threat_level == threat_level)
    return q.order_by(models.DetectionLog.detected_at.desc()).limit(limit).all()


# ── Alert Logs ────────────────────────────────────────────────────────────────

@app.get("/api/alerts")
def get_alerts(
    resolved: Optional[bool] = Query(default=None),
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(auth.get_current_admin)
):
    q = db.query(models.AlertLog)
    if resolved is not None:
        q = q.filter(models.AlertLog.is_resolved == resolved)
    return q.order_by(models.AlertLog.created_at.desc()).limit(100).all()


@app.put("/api/alerts/{alert_id}/resolve")
def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(auth.get_current_admin)
):
    alert = db.query(models.AlertLog).filter(models.AlertLog.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.is_resolved = True
    db.commit()
    return {"msg": "Resolved"}


@app.post("/api/alerts/emergency")
def trigger_emergency(
    message: str = Form(default="EMERGENCY MODE ACTIVATED"),
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(auth.get_current_admin)
):
    alert = models.AlertLog(
        alert_type="Emergency",
        severity="Critical",
        message=message,
        camera_location="All Cameras"
    )
    db.add(alert)
    db.commit()
    return {"msg": "Emergency alert triggered", "alert_id": alert.id}


# ── Camera Management ─────────────────────────────────────────────────────────

@app.get("/api/cameras")
def get_cameras(db: Session = Depends(get_db), current_admin: models.Admin = Depends(auth.get_current_admin)):
    return db.query(models.Camera).all()


@app.post("/api/cameras", status_code=201)
def create_camera(
    name: str = Form(...),
    location: str = Form(...),
    ip_address: str = Form(default=""),
    camera_type: str = Form(default="IP"),
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(auth.get_current_admin)
):
    cam = models.Camera(
        name=name, location=location,
        ip_address=ip_address or None,
        camera_type=camera_type
    )
    db.add(cam)
    db.commit()
    return {"msg": "Camera added", "id": cam.id}


@app.delete("/api/cameras/{camera_id}")
def delete_camera(camera_id: int, db: Session = Depends(get_db), current_admin: models.Admin = Depends(auth.get_current_admin)):
    cam = db.query(models.Camera).filter(models.Camera.id == camera_id).first()
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    db.delete(cam)
    db.commit()
    return {"msg": "Deleted"}


# ── Analytics ─────────────────────────────────────────────────────────────────

@app.get("/api/analytics/trends")
def get_trends(
    days: int = Query(default=7),
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(auth.get_current_admin)
):
    result = []
    for i in range(days - 1, -1, -1):
        d = datetime.date.today() - datetime.timedelta(days=i)
        count = db.query(models.DetectionLog).filter(
            func.date(models.DetectionLog.detected_at) == d
        ).count()
        result.append({"date": d.strftime("%b %d"), "detections": count})
    return result


@app.get("/api/analytics/threat-distribution")
def get_threat_distribution(db: Session = Depends(get_db), current_admin: models.Admin = Depends(auth.get_current_admin)):
    levels = ["Low", "Medium", "High", "Critical"]
    result = []
    for level in levels:
        count = db.query(models.Criminal).filter(models.Criminal.threat_level == level).count()
        result.append({"level": level, "count": count})
    return result


@app.get("/api/analytics/camera-activity")
def get_camera_activity(db: Session = Depends(get_db), current_admin: models.Admin = Depends(auth.get_current_admin)):
    cameras = db.query(models.Camera).all()
    result = []
    for cam in cameras:
        count = db.query(models.DetectionLog).filter(models.DetectionLog.camera_id == cam.id).count()
        result.append({"camera": cam.name, "detections": count})
    return result


@app.get("/api/analytics/geo-data")
def get_geo_data(db: Session = Depends(get_db), current_admin: models.Admin = Depends(auth.get_current_admin)):
    criminals = db.query(models.Criminal).filter(
        models.Criminal.latitude != None,
        models.Criminal.longitude != None
    ).all()
    return [
        {
            "id": c.id, "name": c.name, "threat_level": c.threat_level,
            "lat": c.latitude, "lng": c.longitude,
            "location": c.last_seen_location
        }
        for c in criminals
    ]


# ── AI Chat Assistant ─────────────────────────────────────────────────────────

@app.post("/api/chat")
def ai_chat(query: schemas.ChatQuery, db: Session = Depends(get_db), current_admin: models.Admin = Depends(auth.get_current_admin)):
    q = query.query.lower().strip()
    response = {"type": "text", "data": None, "message": ""}

    # Parse intent
    if any(w in q for w in ["high risk", "high-risk", "critical", "dangerous"]):
        criminals = db.query(models.Criminal).filter(
            models.Criminal.threat_level.in_(["High", "Critical"])
        ).order_by(models.Criminal.threat_level.desc()).all()
        response["type"] = "criminals"
        response["data"] = [{"id": c.id, "name": c.name, "threat_level": c.threat_level, "fir_number": c.fir_number, "case_status": c.case_status} for c in criminals]
        response["message"] = f"Found {len(criminals)} high-risk / critical threat criminals."

    elif any(w in q for w in ["wanted", "active"]):
        criminals = db.query(models.Criminal).filter(models.Criminal.case_status == "Wanted").all()
        response["type"] = "criminals"
        response["data"] = [{"id": c.id, "name": c.name, "threat_level": c.threat_level, "fir_number": c.fir_number, "case_status": c.case_status} for c in criminals]
        response["message"] = f"Found {len(criminals)} wanted criminals."

    elif any(w in q for w in ["alert", "alarm", "unresolved"]):
        alerts = db.query(models.AlertLog).filter(models.AlertLog.is_resolved == False).order_by(models.AlertLog.created_at.desc()).limit(10).all()
        response["type"] = "alerts"
        response["data"] = [{"id": a.id, "message": a.message, "severity": a.severity, "created_at": a.created_at.isoformat()} for a in alerts]
        response["message"] = f"There are {len(alerts)} unresolved alerts."

    elif any(w in q for w in ["detection", "detected", "today"]):
        today = datetime.date.today()
        logs = db.query(models.DetectionLog).filter(
            func.date(models.DetectionLog.detected_at) == today
        ).order_by(models.DetectionLog.detected_at.desc()).all()
        response["type"] = "detections"
        response["data"] = [{"id": l.id, "criminal_name": l.criminal_name or "Unknown", "confidence": l.confidence, "location": l.camera_location, "time": l.detected_at.strftime("%H:%M")} for l in logs]
        response["message"] = f"Today's detections: {len(logs)} total."

    elif any(w in q for w in ["stat", "summary", "overview", "report"]):
        today = datetime.date.today()
        stats = {
            "total_criminals": db.query(models.Criminal).count(),
            "wanted": db.query(models.Criminal).filter(models.Criminal.case_status == "Wanted").count(),
            "active_alerts": db.query(models.AlertLog).filter(models.AlertLog.is_resolved == False).count(),
            "detections_today": db.query(models.DetectionLog).filter(func.date(models.DetectionLog.detected_at) == today).count(),
            "cameras_online": db.query(models.Camera).filter(models.Camera.status == "Online").count(),
        }
        response["type"] = "stats"
        response["data"] = stats
        response["message"] = "Here is the current system summary."

    elif "fir" in q:
        # Extract FIR number
        match = re.search(r'fir[:\s#-]*([a-z0-9\-/]+)', q, re.IGNORECASE)
        if match:
            fir = match.group(1).upper()
            criminal = db.query(models.Criminal).filter(models.Criminal.fir_number.contains(fir)).first()
            if criminal:
                response["type"] = "criminals"
                response["data"] = [{"id": criminal.id, "name": criminal.name, "threat_level": criminal.threat_level, "fir_number": criminal.fir_number, "case_status": criminal.case_status}]
                response["message"] = f"Found criminal record for FIR {criminal.fir_number}."
            else:
                response["message"] = f"No record found for FIR number matching '{fir}'."
        else:
            response["message"] = "Please specify a FIR number, e.g., 'Search FIR-2024-001'."

    else:
        # Fallback: search by name
        words = [w for w in q.split() if len(w) > 2]
        found = []
        for word in words:
            results = db.query(models.Criminal).filter(
                models.Criminal.name.contains(word) |
                models.Criminal.alias.contains(word)
            ).all()
            found.extend(results)

        if found:
            unique = {c.id: c for c in found}
            response["type"] = "criminals"
            response["data"] = [{"id": c.id, "name": c.name, "threat_level": c.threat_level, "fir_number": c.fir_number, "case_status": c.case_status} for c in unique.values()]
            response["message"] = f"Found {len(unique)} matching criminal record(s)."
        else:
            response["message"] = (
                "I can help you with:\n"
                "• 'Show high-risk criminals'\n"
                "• 'Show all wanted persons'\n"
                "• 'Show today's detections'\n"
                "• 'Show active alerts'\n"
                "• 'System summary'\n"
                "• 'Search FIR-2024-001'\n"
                "• '[Criminal name]'"
            )

    return response


# ── Staff (Legacy) ────────────────────────────────────────────────────────────

@app.post("/api/staff")
async def create_staff(
    name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    department_or_role: str = Form(...),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(auth.get_current_admin)
):
    try:
        unique_name = f"{name.replace(' ', '_')}_{photo.filename}"
        upload_dir = STATIC_DIR / "uploads" / "staff"
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_location = upload_dir / unique_name
        with open(file_location, "wb+") as f:
            shutil.copyfileobj(photo.file, f)

        db_staff = models.AuthorizedStaff(
            name=name, age=age, gender=gender,
            department_or_role=department_or_role,
            image_path=f"/static/uploads/staff/{unique_name}"
        )
        db.add(db_staff)
        db.commit()
        db.refresh(db_staff)

        success = vision.process_and_save_face(str(file_location), db_staff.id)
        if not success:
            db.delete(db_staff)
            db.commit()
            if file_location.exists():
                file_location.unlink()
            raise HTTPException(status_code=400, detail="No valid face detected.")

        vision.train_recognizer()
        return {"msg": "Success", "staff_id": db_staff.id}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/staff")
def get_staff(db: Session = Depends(get_db), current_admin: models.Admin = Depends(auth.get_current_admin)):
    return db.query(models.AuthorizedStaff).all()


@app.delete("/api/staff/{staff_id}")
def delete_staff(staff_id: int, db: Session = Depends(get_db), current_admin: models.Admin = Depends(auth.get_current_admin)):
    staff = db.query(models.AuthorizedStaff).filter(models.AuthorizedStaff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    db.delete(staff)
    db.commit()
    dataset_path = BASE_DIR / "dataset" / f"{staff_id}.jpg"
    if dataset_path.exists():
        dataset_path.unlink()
    vision.train_recognizer()
    return {"msg": "Deleted"}


# ── CSV Export Endpoint ───────────────────────────────────────────────────────

@app.get("/api/criminals/export/csv")
def export_criminals_csv(db: Session = Depends(get_db)):
    criminals = db.query(models.Criminal).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Name", "Alias", "Age", "Gender", "FIR Number",
        "Threat Level", "Case Status", "Last Seen Location", "Nationality", "Notes"
    ])
    for c in criminals:
        writer.writerow([
            c.id, c.name, c.alias or "", c.age or "", c.gender or "", c.fir_number or "",
            c.threat_level or "", c.case_status or "", c.last_seen_location or "", c.nationality or "", c.notes or ""
        ])
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=criminals_export_{datetime.date.today()}.csv"}
    )


# ── Printable Evidence PDF/HTML Report ────────────────────────────────────────

@app.get("/api/reports/pdf/{detection_id}")
def generate_detection_report(detection_id: int, db: Session = Depends(get_db)):
    log = db.query(models.DetectionLog).filter(models.DetectionLog.id == detection_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Detection log not found")

    criminal = None
    if log.criminal_id:
        criminal = db.query(models.Criminal).filter(models.Criminal.id == log.criminal_id).first()

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <title>CFCS Evidence Report - Log #{log.id}</title>
      <style>
        body {{ font-family: 'Helvetica Neue', Arial, sans-serif; background: #fff; color: #111; padding: 40px; line-height: 1.6; }}
        .header {{ display: flex; justify-content: space-between; border-bottom: 2px solid #000; padding-bottom: 20px; margin-bottom: 30px; }}
        .title {{ font-size: 24px; font-weight: bold; letter-spacing: -0.5px; }}
        .sub {{ font-size: 12px; color: #666; text-transform: uppercase; margin-top: 4px; }}
        .section {{ margin-bottom: 30px; }}
        .section h3 {{ font-size: 16px; border-bottom: 1px solid #ccc; padding-bottom: 6px; margin-bottom: 12px; text-transform: uppercase; font-size: 12px; letter-spacing: 1px; color: #444; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ padding: 10px 14px; text-align: left; border-bottom: 1px solid #eee; font-size: 14px; }}
        th {{ background: #f8f9fa; font-weight: 600; color: #333; }}
        .badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; background: #ef4444; color: #fff; }}
        .footer {{ border-top: 1px solid #ddd; margin-top: 50px; padding-top: 16px; text-align: center; font-size: 11px; color: #888; }}
      </style>
    </head>
    <body>
      <div class="header">
        <div>
          <div class="title">CFCS LAW ENFORCEMENT EVIDENCE REPORT</div>
          <div class="sub">CONFIDENTIAL SURVEILLANCE LOG RECORD #{log.id}</div>
        </div>
        <div style="text-align: right;">
          <div style="font-weight: bold;">TIMESTAMP</div>
          <div>{log.detected_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</div>
        </div>
      </div>

      <div class="section">
        <h3>Detection Event Details</h3>
        <table>
          <tr><th>Log ID</th><td>#{log.id}</td><th>Camera Location</th><td>{log.camera_location or 'CCTV Feed #1'}</td></tr>
          <tr><th>Match Confidence</th><td><strong>{log.confidence:.1f}%</strong></td><th>Threat Level</th><td><span class="badge">{log.threat_level or 'HIGH'}</span></td></tr>
          <tr><th>Age Estimate</th><td>{log.age_estimate or 'N/A'}</td><th>Gender Estimate</th><td>{log.gender_estimate or 'N/A'}</td></tr>
          <tr><th>Review Status</th><td>{log.status}</td><th>Timestamp</th><td>{log.detected_at.strftime('%c')}</td></tr>
        </table>
      </div>

      <div class="section">
        <h3>Criminal Profile Match</h3>
        <table>
          <tr><th>Name</th><td><strong>{criminal.name if criminal else log.criminal_name or 'Unknown Person'}</strong></td></tr>
          <tr><th>Alias</th><td>{criminal.alias if criminal else 'N/A'}</td></tr>
          <tr><th>FIR Number</th><td>{criminal.fir_number if criminal else 'N/A'}</td></tr>
          <tr><th>Case Status</th><td>{criminal.case_status if criminal else 'Active Investigation'}</td></tr>
          <tr><th>Last Known Address</th><td>{criminal.address if criminal else 'N/A'}</td></tr>
        </table>
      </div>

      <div class="footer">
        Generated automatically by CFCS v2.0 AI Law Enforcement Surveillance System. Strictly for Official Police Use Only.
      </div>
      <script>window.onload = function() {{ window.print(); }};</script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


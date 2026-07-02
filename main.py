from fastapi import FastAPI, Depends, HTTPException, Request, status, Form, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import os
import shutil

import models
import schemas
import auth
import vision
from database import engine, Base, get_db

Base.metadata.create_all(bind=engine)
app = FastAPI(title="CFCS")

os.makedirs("static/uploads/staff", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# pages
@app.get("/")
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {"request": request})

@app.get("/dashboard")
async def dashboard_page(request: Request):
    return templates.TemplateResponse(request, "dashboard.html", {"request": request})

@app.get("/staff_page")
async def staff_page(request: Request):
    return templates.TemplateResponse(request, "staff.html", {"request": request})

@app.get("/recognition_page")
async def recognition_page(request: Request):
    return templates.TemplateResponse(request, "recognition.html", {"request": request})

# APIs

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    admin = db.query(models.Admin).filter(models.Admin.username == form_data.username).first()
    if not admin or not auth.verify_password(form_data.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": admin.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db), current_admin: models.Admin = Depends(auth.get_current_admin)):
    total = db.query(models.AuthorizedStaff).count()
    return {"total_staff": total}

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
        # Save photo
        ext = photo.filename.split(".")[-1]
        unique_name = f"{name.replace(' ', '_')}_{photo.filename}"
        file_location = f"static/uploads/staff/{unique_name}"
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(photo.file, file_object)
        
        # Save staff to DB temporarily to get ID
        db_staff = models.AuthorizedStaff(
            name=name,
            age=age,
            gender=gender,
            department_or_role=department_or_role,
            image_path=f"/{file_location}"
        )
        db.add(db_staff)
        db.commit()
        db.refresh(db_staff)
        
        # Process face encoding
        success = vision.process_and_save_face(file_location, db_staff.id)
        if not success:
            db.delete(db_staff)
            db.commit()
            if os.path.exists(file_location):
                os.remove(file_location)
            raise HTTPException(status_code=400, detail="No valid face detected. Please ensure the photo is clear and contains exactly one frontal face.")
        
        # Train LBPH immediately
        vision.train_recognizer()
        
        return {"msg": "Success", "staff_id": db_staff.id}
    except HTTPException as he:
        raise he
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/api/staff")
def get_staff(db: Session = Depends(get_db), current_admin: models.Admin = Depends(auth.get_current_admin)):
    staff = db.query(models.AuthorizedStaff).all()
    return staff

@app.delete("/api/staff/{staff_id}")
def delete_staff(staff_id: int, db: Session = Depends(get_db), current_admin: models.Admin = Depends(auth.get_current_admin)):
    staff = db.query(models.AuthorizedStaff).filter(models.AuthorizedStaff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    db.delete(staff)
    db.commit()
    # Also delete dataset image and retrain
    dataset_path = f"dataset/{staff_id}.jpg"
    if os.path.exists(dataset_path):
        os.remove(dataset_path)
    vision.train_recognizer()
    return {"msg": "Deleted"}

@app.post("/api/recognize")
async def recognize_uploaded_face(
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(auth.get_current_admin)
):
    try:
        os.makedirs("static/uploads/temp", exist_ok=True)
        temp_path = f"static/uploads/temp/{photo.filename}"
        with open(temp_path, "wb+") as f:
            shutil.copyfileobj(photo.file, f)
        
        criminal_id, accuracy = vision.recognize_face(temp_path)
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        if criminal_id is None:
            return {"match": False, "message": "No obvious face found or no matching dataset available."}
            
        # fetch staff details
        staff = db.query(models.AuthorizedStaff).filter(models.AuthorizedStaff.id == criminal_id).first()
        if staff and accuracy > 10: # Minimum acceptable accuracy
            return {
                "match": True,
                "staff": {
                    "id": staff.id,
                    "name": staff.name,
                    "age": staff.age,
                    "gender": staff.gender,
                    "department_or_role": staff.department_or_role,
                    "image_path": staff.image_path
                },
                "accuracy": round(accuracy, 2)
            }
        
        return {"match": False, "message": "Access Denied - Security Alert: Unauthorized individual detected."}
        
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

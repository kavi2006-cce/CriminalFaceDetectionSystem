from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON
from database import Base
import datetime


class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="admin")  # admin / officer
    full_name = Column(String, default="Administrator")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class AuthorizedStaff(Base):
    __tablename__ = "staff"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    gender = Column(String)
    department_or_role = Column(Text)
    image_path = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Criminal(Base):
    __tablename__ = "criminals"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    alias = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String, default="Unknown")
    fir_number = Column(String, unique=True, index=True, nullable=True)
    crime_history = Column(Text, nullable=True)
    case_status = Column(String, default="Active")  # Active / Closed / Wanted / Arrested
    threat_level = Column(String, default="Medium")  # Low / Medium / High / Critical
    last_seen_location = Column(String, nullable=True)
    last_seen_at = Column(DateTime, nullable=True)
    nationality = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    phone = Column(String, nullable=True)
    image_path = Column(String, nullable=True)  # Primary photo
    notes = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class Camera(Base):
    __tablename__ = "cameras"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    location = Column(String)
    ip_address = Column(String, nullable=True)
    status = Column(String, default="Online")  # Online / Offline / Maintenance
    camera_type = Column(String, default="IP")  # IP / USB / RTSP
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class DetectionLog(Base):
    __tablename__ = "detection_logs"
    id = Column(Integer, primary_key=True, index=True)
    criminal_id = Column(Integer, nullable=True)  # NULL = unknown person
    criminal_name = Column(String, nullable=True)
    camera_id = Column(Integer, nullable=True)
    camera_location = Column(String, nullable=True)
    confidence = Column(Float, default=0.0)
    threat_level = Column(String, default="Unknown")
    screenshot_path = Column(String, nullable=True)
    age_estimate = Column(Integer, nullable=True)
    gender_estimate = Column(String, nullable=True)
    is_unknown = Column(Boolean, default=False)
    status = Column(String, default="New")  # New / Reviewed / Dismissed
    detected_at = Column(DateTime, default=datetime.datetime.utcnow)


class AlertLog(Base):
    __tablename__ = "alert_logs"
    id = Column(Integer, primary_key=True, index=True)
    detection_id = Column(Integer, nullable=True)
    criminal_id = Column(Integer, nullable=True)
    criminal_name = Column(String, nullable=True)
    alert_type = Column(String, default="Detection")  # Detection / Emergency / System
    severity = Column(String, default="High")  # Low / Medium / High / Critical
    message = Column(Text)
    camera_location = Column(String, nullable=True)
    email_sent = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

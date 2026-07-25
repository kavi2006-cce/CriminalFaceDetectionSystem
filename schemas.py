from pydantic import BaseModel
from typing import Optional, List
import datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# ── Criminal Schemas ─────────────────────────────────────────────────────────

class CriminalCreate(BaseModel):
    name: str
    alias: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = "Unknown"
    fir_number: Optional[str] = None
    crime_history: Optional[str] = None
    case_status: Optional[str] = "Active"
    threat_level: Optional[str] = "Medium"
    last_seen_location: Optional[str] = None
    nationality: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class CriminalUpdate(BaseModel):
    name: Optional[str] = None
    alias: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    fir_number: Optional[str] = None
    crime_history: Optional[str] = None
    case_status: Optional[str] = None
    threat_level: Optional[str] = None
    last_seen_location: Optional[str] = None
    nationality: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class CriminalOut(BaseModel):
    id: int
    name: str
    alias: Optional[str]
    age: Optional[int]
    gender: str
    fir_number: Optional[str]
    crime_history: Optional[str]
    case_status: str
    threat_level: str
    last_seen_location: Optional[str]
    nationality: Optional[str]
    image_path: Optional[str]
    notes: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# ── Camera Schemas ────────────────────────────────────────────────────────────

class CameraCreate(BaseModel):
    name: str
    location: str
    ip_address: Optional[str] = None
    camera_type: Optional[str] = "IP"
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class CameraOut(BaseModel):
    id: int
    name: str
    location: str
    ip_address: Optional[str]
    status: str
    camera_type: str
    latitude: Optional[float]
    longitude: Optional[float]
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# ── Detection Log Schemas ─────────────────────────────────────────────────────

class DetectionLogOut(BaseModel):
    id: int
    criminal_id: Optional[int]
    criminal_name: Optional[str]
    camera_id: Optional[int]
    camera_location: Optional[str]
    confidence: float
    threat_level: str
    screenshot_path: Optional[str]
    age_estimate: Optional[int]
    gender_estimate: Optional[str]
    is_unknown: bool
    status: str
    detected_at: datetime.datetime

    class Config:
        from_attributes = True


# ── Alert Log Schemas ─────────────────────────────────────────────────────────

class AlertLogOut(BaseModel):
    id: int
    detection_id: Optional[int]
    criminal_id: Optional[int]
    criminal_name: Optional[str]
    alert_type: str
    severity: str
    message: str
    camera_location: Optional[str]
    email_sent: bool
    is_resolved: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# ── Chat ──────────────────────────────────────────────────────────────────────

class ChatQuery(BaseModel):
    query: str


# ── Stats ─────────────────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_criminals: int
    active_alerts: int
    cameras_online: int
    detections_today: int
    high_threat_count: int
    unknown_persons_today: int

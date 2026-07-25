"""
CFCS v2.0 — Database Seeder
Populates the database with:
  - Default admin account (admin / admin123)
  - Sample criminals with varying threat levels
  - Sample cameras
  - Sample detection logs and alerts

Run: python seed_db.py
"""

import sys
import os
import datetime

sys.path.insert(0, os.path.dirname(__file__))

from database import engine, Base, SessionLocal
import models
from sqlalchemy import text

Base.metadata.create_all(bind=engine)
db = SessionLocal()


def seed():
    print("🌱 Seeding CFCS database…")

    # ── Auto Schema Migration Check ────────────────────────────────────────────
    for stmt in [
        "ALTER TABLE admins ADD COLUMN role VARCHAR DEFAULT 'admin'",
        "ALTER TABLE admins ADD COLUMN full_name VARCHAR DEFAULT 'Administrator'",
        "ALTER TABLE criminals ADD COLUMN address TEXT",
        "ALTER TABLE criminals ADD COLUMN notes TEXT"
    ]:
        try:
            db.execute(text(stmt))
            db.commit()
        except Exception:
            db.rollback()

    # ── Admin ─────────────────────────────────────────────────────────────────
    existing_admin = db.query(models.Admin).filter(models.Admin.username == "admin").first()
    if not existing_admin:
        admin = models.Admin(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            full_name="System Administrator"
        )
        db.add(admin)
        db.commit()
        print("  ✅ Admin created — username: admin / password: admin123")
    else:
        print("  ℹ️  Admin already exists — skipping")

    # ── Criminals ─────────────────────────────────────────────────────────────
    criminal_count = db.query(models.Criminal).count()
    if criminal_count == 0:
        criminals = [
            models.Criminal(
                name="Rajan Subramaniam",
                alias="Raja Bhai",
                age=38,
                gender="Male",
                fir_number="FIR-2024-001",
                crime_history="Armed robbery (2019), assault with deadly weapon (2021), bank robbery attempt (2023). Known to operate with a gang of 4 members.",
                case_status="Wanted",
                threat_level="Critical",
                last_seen_location="Tambaram, Chennai, Tamil Nadu",
                nationality="Indian",
                notes="Extremely dangerous. Believed to be armed. Do not approach alone.",
                latitude=12.9249,
                longitude=80.1000,
                last_seen_at=datetime.datetime.utcnow() - datetime.timedelta(days=3)
            ),
            models.Criminal(
                name="Priya Devi",
                alias="Black Rose",
                age=29,
                gender="Female",
                fir_number="FIR-2024-002",
                crime_history="Cybercrime, financial fraud (2022), identity theft (2023). Operates online banking scams targeting senior citizens.",
                case_status="Active",
                threat_level="High",
                last_seen_location="Koramangala, Bengaluru, Karnataka",
                nationality="Indian",
                notes="Tech-savvy. Uses multiple SIM cards and VPNs.",
                latitude=12.9352,
                longitude=77.6245,
                last_seen_at=datetime.datetime.utcnow() - datetime.timedelta(days=7)
            ),
            models.Criminal(
                name="Mohammed Ismail",
                alias="Iron Fist",
                age=45,
                gender="Male",
                fir_number="FIR-2023-087",
                crime_history="Drug trafficking (2020), money laundering (2021, 2022). Interpol red notice issued. International connections suspected.",
                case_status="Wanted",
                threat_level="Critical",
                last_seen_location="Dharavi, Mumbai, Maharashtra",
                nationality="Indian",
                notes="International links. May attempt to flee the country. High priority target.",
                latitude=19.0390,
                longitude=72.8540,
                last_seen_at=datetime.datetime.utcnow() - datetime.timedelta(hours=18)
            ),
            models.Criminal(
                name="Karthik Nair",
                alias="Shadow",
                age=31,
                gender="Male",
                fir_number="FIR-2024-034",
                crime_history="Pickpocketing (2018), chain snatching (2019, 2020), vehicle theft (2022).",
                case_status="Active",
                threat_level="Medium",
                last_seen_location="T. Nagar, Chennai, Tamil Nadu",
                nationality="Indian",
                notes="Usually operates in crowded market areas. Quick getaway using motorcycles.",
                latitude=13.0418,
                longitude=80.2341,
                last_seen_at=datetime.datetime.utcnow() - datetime.timedelta(days=1)
            ),
            models.Criminal(
                name="Sunita Sharma",
                alias="Madam S",
                age=52,
                gender="Female",
                fir_number="FIR-2023-112",
                crime_history="Human trafficking (2018), forced labor exploitation (2020). Runs underground network across 3 states.",
                case_status="Wanted",
                threat_level="Critical",
                last_seen_location="Mehrauli, New Delhi",
                nationality="Indian",
                notes="Travels frequently. Known disguises. Contact state border police.",
                latitude=28.5245,
                longitude=77.1855,
                last_seen_at=datetime.datetime.utcnow() - datetime.timedelta(days=14)
            ),
            models.Criminal(
                name="Vijay Kumar",
                alias="VK",
                age=27,
                gender="Male",
                fir_number="FIR-2024-056",
                crime_history="Vandalism (2021), shoplifting (2022), minor assault (2023).",
                case_status="Arrested",
                threat_level="Low",
                last_seen_location="Anna Nagar, Chennai, Tamil Nadu",
                nationality="Indian",
                notes="Currently in custody. Case under trial.",
                latitude=13.0850,
                longitude=80.2101,
            ),
            models.Criminal(
                name="Deepak Joshi",
                alias="DJ",
                age=35,
                gender="Male",
                fir_number="FIR-2023-199",
                crime_history="Extortion (2019, 2021), illegal firearms possession (2022). Gang leader.",
                case_status="Wanted",
                threat_level="High",
                last_seen_location="Hyderabad, Telangana",
                nationality="Indian",
                notes="Gang of 8. Targets small business owners for protection money.",
                latitude=17.3850,
                longitude=78.4867,
                last_seen_at=datetime.datetime.utcnow() - datetime.timedelta(days=5)
            ),
            models.Criminal(
                name="Anita Kumari",
                alias="Anita",
                age=24,
                gender="Female",
                fir_number="FIR-2024-078",
                crime_history="Credit card fraud (2023). Cloned 47 credit cards targeting ATM users.",
                case_status="Active",
                threat_level="Medium",
                last_seen_location="Connaught Place, New Delhi",
                nationality="Indian",
                notes="Uses skimming devices. Possibly working with a larger network.",
                latitude=28.6315,
                longitude=77.2167,
                last_seen_at=datetime.datetime.utcnow() - datetime.timedelta(days=2)
            ),
        ]
        for c in criminals:
            db.add(c)
        db.commit()
        print(f"  ✅ {len(criminals)} criminal records added")
    else:
        print(f"  ℹ️  {criminal_count} criminals already exist — skipping")

    # ── Cameras ───────────────────────────────────────────────────────────────
    cam_count = db.query(models.Camera).count()
    if cam_count == 0:
        cameras = [
            models.Camera(name="Main Gate CAM-01", location="Main Gate, North Entrance", ip_address="192.168.1.101", camera_type="IP", status="Online", latitude=13.0827, longitude=80.2707),
            models.Camera(name="Lobby CAM-02", location="Building A, Lobby", ip_address="192.168.1.102", camera_type="IP", status="Online", latitude=13.0830, longitude=80.2710),
            models.Camera(name="Parking CAM-03", location="Underground Parking Level B1", ip_address="192.168.1.103", camera_type="IP", status="Offline", latitude=13.0820, longitude=80.2700),
            models.Camera(name="Exit CAM-04", location="South Exit, Gate 3", ip_address="192.168.1.104", camera_type="IP", status="Online", latitude=13.0815, longitude=80.2695),
            models.Camera(name="Corridor CAM-05", location="Floor 2, East Corridor", ip_address="192.168.1.105", camera_type="IP", status="Online"),
        ]
        for c in cameras:
            db.add(c)
        db.commit()
        print(f"  ✅ {len(cameras)} cameras added")
    else:
        print(f"  ℹ️  {cam_count} cameras already exist — skipping")

    # ── Detection Logs ────────────────────────────────────────────────────────
    log_count = db.query(models.DetectionLog).count()
    if log_count == 0:
        criminals_in_db = db.query(models.Criminal).all()
        cameras_in_db  = db.query(models.Camera).all()

        now = datetime.datetime.utcnow()
        logs = []

        for i, c in enumerate(criminals_in_db[:4]):
            cam = cameras_in_db[i % len(cameras_in_db)]
            logs.append(models.DetectionLog(
                criminal_id=c.id,
                criminal_name=c.name,
                camera_id=cam.id,
                camera_location=cam.location,
                confidence=72.0 + i * 4.5,
                threat_level=c.threat_level,
                is_unknown=False,
                status="New",
                detected_at=now - datetime.timedelta(hours=i * 3)
            ))

        # Some unknown persons
        for i in range(3):
            cam = cameras_in_db[i % len(cameras_in_db)]
            logs.append(models.DetectionLog(
                camera_id=cam.id,
                camera_location=cam.location,
                confidence=0,
                threat_level="Unknown",
                is_unknown=True,
                status="Reviewed",
                detected_at=now - datetime.timedelta(hours=i + 1)
            ))

        for log in logs:
            db.add(log)
        db.commit()
        print(f"  ✅ {len(logs)} detection logs added")
    else:
        print(f"  ℹ️  {log_count} detection logs already exist — skipping")

    # ── Alert Logs ────────────────────────────────────────────────────────────
    alert_count = db.query(models.AlertLog).count()
    if alert_count == 0:
        criminals_in_db = db.query(models.Criminal).all()
        cameras_in_db  = db.query(models.Camera).all()
        now = datetime.datetime.utcnow()

        alerts = []
        for i, c in enumerate(criminals_in_db[:3]):
            cam = cameras_in_db[i % len(cameras_in_db)]
            alerts.append(models.AlertLog(
                criminal_id=c.id,
                criminal_name=c.name,
                alert_type="Detection",
                severity=c.threat_level,
                message=f"Criminal '{c.name}' (FIR: {c.fir_number}) detected at {cam.location} with {72 + i*4}% confidence.",
                camera_location=cam.location,
                is_resolved=i > 0,
                created_at=now - datetime.timedelta(hours=i * 4)
            ))

        alerts.append(models.AlertLog(
            alert_type="System",
            severity="Medium",
            message="Camera 'Parking CAM-03' went offline. Maintenance required.",
            camera_location="Underground Parking Level B1",
            is_resolved=False,
            created_at=now - datetime.timedelta(hours=6)
        ))

        for a in alerts:
            db.add(a)
        db.commit()
        print(f"  ✅ {len(alerts)} alert logs added")
    else:
        print(f"  ℹ️  {alert_count} alerts already exist — skipping")

    db.close()
    print("\n✅ Database seeding complete!")
    print("   Login with: admin / admin123")
    print("   Start server: uvicorn main:app --reload")
    print("   Open: http://localhost:8000")


if __name__ == "__main__":
    seed()

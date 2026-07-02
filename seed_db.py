import database
import models
import auth

db = database.SessionLocal()
if not db.query(models.Admin).filter(models.Admin.username == "admin").first():
    admin = models.Admin(
        username="admin",
        hashed_password=auth.get_password_hash("admin123")
    )
    db.add(admin)
    db.commit()
    print("Admin user created (admin / admin123)")
else:
    print("Admin already exists")

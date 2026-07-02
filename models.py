from sqlalchemy import Column, Integer, String, Text, DateTime
from database import Base
import datetime

class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class AuthorizedStaff(Base):
    __tablename__ = "staff"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    gender = Column(String)
    department_or_role = Column(Text)
    image_path = Column(String)  # Path to the actual photo
    # For OpenCV LBPH, we often need a numeric label or we can just train using the id
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

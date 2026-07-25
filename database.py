from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Determine if running in Vercel or read-only serverless environment
is_serverless = bool(
    os.environ.get("VERCEL") or 
    os.environ.get("VERCEL_ENV") or 
    os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
)

if is_serverless:
    SQLALCHEMY_DATABASE_URL = "sqlite:////tmp/cfcs.db"
else:
    try:
        test_file = "./.write_test"
        with open(test_file, "w") as f:
            f.write("1")
        os.remove(test_file)
        SQLALCHEMY_DATABASE_URL = "sqlite:///./cfcs.db"
    except Exception:
        SQLALCHEMY_DATABASE_URL = "sqlite:////tmp/cfcs.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

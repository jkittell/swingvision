import logging
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from minio import Minio
from functools import lru_cache

# Configure console handler for errors only
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.ERROR)
console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))

# Create a logger object for this module
logger = logging.getLogger(__name__)

# Database configuration
CRATE_HOST = "localhost"
CRATE_PORT = 4200
DATABASE_URL = f"crate://{CRATE_HOST}:{CRATE_PORT}"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# MinIO configuration
MINIO_HOST = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"  # Change in production
MINIO_SECRET_KEY = "minioadmin"  # Change in production
MINIO_BUCKET = "swingvision-videos"
MINIO_SECURE = False  # Set to True for HTTPS

@lru_cache
def get_minio_client():
    """Get MinIO client instance"""
    client = Minio(
        MINIO_HOST,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE
    )
    
    # Ensure bucket exists
    if not client.bucket_exists(MINIO_BUCKET):
        client.make_bucket(MINIO_BUCKET)
        
    return client

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
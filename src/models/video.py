from sqlalchemy import Column, String, DateTime, Integer
from src.config import Base
from datetime import datetime

class Video(Base):
    __tablename__ = "videos"
    
    id = Column(String, primary_key=True)
    filename = Column(String)
    content_type = Column(String)
    size = Column(Integer)
    bucket = Column(String)
    object_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
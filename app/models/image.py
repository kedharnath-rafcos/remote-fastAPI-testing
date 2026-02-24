"""
Image database model for storing image metadata.
"""
from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Table
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base
from uuid import UUID
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid


class Image(Base):
    """Image model for database."""
    
    __tablename__ = "images"
    __table_args__ = {'extend_existing': True, 'autoload_with': None}
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_id = Column(String(100), unique=True, nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    s3_key = Column(String(500), nullable=False)  # Full S3 object key
    s3_url = Column(String(1000), nullable=False)  # Full S3 URL
    variants = Column(JSONB, nullable=True)  # All variant URLs (original, thumbnail, small, medium, large)
    file_size = Column(BigInteger, nullable=True)  # Size in bytes
    content_type = Column(String(100), nullable=True)  # MIME type
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Image(id={self.id}, image_id='{self.image_id}', filename='{self.filename}')>"

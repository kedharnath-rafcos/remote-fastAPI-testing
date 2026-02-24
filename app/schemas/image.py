"""
Image Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime
from uuid import UUID


class ImageUploadResponse(BaseModel):
    """Schema for image upload response."""
    image_id: str = Field(..., description="Unique image identifier")
    filename: str = Field(..., description="Original filename")
    s3_key: str = Field(..., description="S3 object key")
    s3_url: str = Field(..., description="Full S3 URL (original)")
    variants: Dict[str, str] = Field(..., description="URLs for all image variants (thumbnail, small, medium, large, original)")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    content_type: Optional[str] = Field(None, description="MIME type")
    message: str = Field(..., description="Success message")
    
    class Config:
        schema_extra = {
            "example": {
                "image_id": "img_abc123_1234567890",
                "filename": "photo.jpg",
                "s3_key": "images/2026/02/20/img_abc123_photo.jpg",
                "s3_url": "https://sports-images-test.s3.eu-north-1.amazonaws.com/images/2026/02/20/img_abc123_photo.jpg",
                "variants": {
                    "original": "https://sports-images-test.s3.eu-north-1.amazonaws.com/images/2026/02/20/img_abc123_photo.jpg",
                    "thumbnail": "https://sports-images-test.s3.eu-north-1.amazonaws.com/images/2026/02/20/img_abc123_photo_thumbnail.jpg",
                    "small": "https://sports-images-test.s3.eu-north-1.amazonaws.com/images/2026/02/20/img_abc123_photo_small.jpg",
                    "medium": "https://sports-images-test.s3.eu-north-1.amazonaws.com/images/2026/02/20/img_abc123_photo_medium.jpg",
                    "large": "https://sports-images-test.s3.eu-north-1.amazonaws.com/images/2026/02/20/img_abc123_photo_large.jpg"
                },
                "file_size": 1234567,
                "content_type": "image/jpeg",
                "message": "Image uploaded successfully"
            }
        }


class ImageBase64Upload(BaseModel):
    """Schema for base64 image upload."""
    filename: str = Field(..., description="Image filename with extension")
    base64_data: str = Field(..., description="Base64 encoded image data")
    content_type: Optional[str] = Field(None, description="MIME type (e.g., image/jpeg)")


class ImageResponse(BaseModel):
    """Schema for image metadata response."""
    id: UUID
    image_id: str
    filename: str
    s3_key: str
    s3_url: str
    variants: Optional[Dict[str, str]] = None
    file_size: Optional[int] = None
    content_type: Optional[str] = None
    created_at: datetime
    
    class Config:
        """Pydantic config."""
        orm_mode = True  # For Pydantic v1


class ImageListResponse(BaseModel):
    """Schema for listing multiple images."""
    count: int
    images: list[ImageResponse]


class ImageDeleteResponse(BaseModel):
    """Schema for image deletion response."""
    image_id: str
    message: str = Field(default="Image deleted successfully")
    deleted_from_s3: bool = Field(default=True)
    deleted_from_db: bool = Field(default=True)


class PresignedUrlResponse(BaseModel):
    """Schema for presigned URL response."""
    image_id: str
    presigned_url: str
    expires_in: int = Field(default=3600, description="URL expiration time in seconds")

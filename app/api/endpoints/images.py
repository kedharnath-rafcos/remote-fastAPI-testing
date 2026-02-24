"""
Image API endpoints for AWS S3 operations.
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Optional
from io import BytesIO

from app.core.database import get_db
from app.models.image import Image
from app.schemas.image import (
    ImageUploadResponse,
    ImageBase64Upload,
    ImageDeleteResponse,
    PresignedUrlResponse,
    ImageResponse,
    ImageListResponse
)
from app.services.s3_service import s3_service


router = APIRouter(
    prefix="/images",
    tags=["Images"]
)


@router.post("/upload", response_model=ImageUploadResponse, status_code=201)
async def upload_image(
    file: UploadFile = File(..., description="Image file to upload"),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload an image file to AWS S3 and save metadata to database.
    
    - **file**: Image file (multipart/form-data)
    - **Allowed formats**: JPG, JPEG, PNG, GIF, WEBP
    - **Max file size**: 10MB
    
    Returns:
        - image_id: Unique identifier for the image
        - filename: Original filename
        - s3_key: S3 object key (path in bucket)
        - s3_url: Full public URL to access the image
        - file_size: Size in bytes
        - content_type: MIME type
    """
    # Upload to S3
    result = await s3_service.upload_file(file)
    
    print(f"📦 Upload result from S3 service: {result}")
    print(f"🎨 Variants in result: {result.get('variants', 'NO VARIANTS!')}")
    
    # Save metadata to database
    try:
        print(f"💾 Creating Image object with variants: {result['variants']}")
        new_image = Image(
            image_id=result['image_id'],
            filename=result['filename'],
            s3_key=result['s3_key'],
            s3_url=result['s3_url'],
            variants=result['variants'],
            file_size=result['file_size'],
            content_type=result['content_type']
        )
        print(f"✅ Image object created. Variants field: {new_image.variants}")
        
        db.add(new_image)
        print(f"✅ Image added to session")
        
        await db.commit()
        print(f"✅ Database commit successful")
        
        await db.refresh(new_image)
        print(f"✅ Image refreshed. Final variants value: {new_image.variants}")
    except Exception as e:
        print(f"❌ ERROR saving to database: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    
    response_data = ImageUploadResponse(
        image_id=result['image_id'],
        filename=result['filename'],
        s3_key=result['s3_key'],
        s3_url=result['s3_url'],
        variants=result['variants'],
        file_size=result['file_size'],
        content_type=result['content_type'],
        message="Image uploaded successfully to S3 with multiple quality variants and saved to database"
    )
    
    print(f"📤 Response being returned: {response_data.dict()}")
    
    return response_data


@router.post("/upload-base64", response_model=ImageUploadResponse, status_code=201)
async def upload_image_base64(
    image_data: ImageBase64Upload,
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a base64 encoded image to AWS S3 and save metadata to database.
    
    - **filename**: Image filename with extension (e.g., "profile.jpg")
    - **base64_data**: Base64 encoded image string
    - **content_type**: MIME type (optional, auto-detected if not provided)
    
    Returns:
        - image_id: Unique identifier for the image
        - filename: Original filename
        - s3_key: S3 object key (path in bucket)
        - s3_url: Full public URL to access the image
        - file_size: Size in bytes
        - content_type: MIME type
    """
    # Upload to S3
    result = await s3_service.upload_base64(
        filename=image_data.filename,
        base64_data=image_data.base64_data,
        content_type=image_data.content_type
    )
    
    print(f"📦 Upload result from S3 service (base64): {result}")
    print(f"🎨 Variants in result (base64): {result.get('variants', 'NO VARIANTS!')}")
    
    # Save metadata to database
    new_image = Image(
        image_id=result['image_id'],
        filename=result['filename'],
        s3_key=result['s3_key'],
        s3_url=result['s3_url'],
        variants=result['variants'],
        file_size=result['file_size'],
        content_type=result['content_type']
    )
    db.add(new_image)
    await db.commit()
    await db.refresh(new_image)
    
    response_data = ImageUploadResponse(
        image_id=result['image_id'],
        filename=result['filename'],
        s3_key=result['s3_key'],
        s3_url=result['s3_url'],
        variants=result['variants'],
        file_size=result['file_size'],
        content_type=result['content_type'],
        message="Base64 image uploaded successfully to S3 with multiple quality variants and saved to database"
    )
    
    print(f"📤 Response being returned (base64): {response_data.dict()}")
    
    return response_data


@router.get("/download/{image_id}")
async def download_image(
    image_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Download an image from AWS S3 using image_id from database.
    
    - **image_id**: Unique image identifier
    
    Returns:
        StreamingResponse with image content
    """
    # Get image metadata from database
    result = await db.execute(
        select(Image).where(Image.image_id == image_id)
    )
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found in database")
    
    # Download from S3
    file_content, content_type = await s3_service.download_file(image.s3_key)
    
    return StreamingResponse(
        BytesIO(file_content),
        media_type=content_type,
        headers={
            "Content-Disposition": f'inline; filename="{image.filename}"'
        }
    )


@router.delete("/{image_id}", response_model=ImageDeleteResponse)
async def delete_image(
    image_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an image from AWS S3 and database.
    
    - **image_id**: Unique image identifier
    
    Returns:
        Deletion confirmation message
    """
    # Get image metadata from database
    result = await db.execute(
        select(Image).where(Image.image_id == image_id)
    )
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found in database")
    
    # Delete from S3
    deleted_from_s3 = await s3_service.delete_file(image.s3_key)
    
    # Delete from database
    await db.execute(
        delete(Image).where(Image.image_id == image_id)
    )
    await db.commit()
    
    return ImageDeleteResponse(
        image_id=image_id,
        message=f"Image {image_id} deleted successfully from S3 and database",
        deleted_from_s3=deleted_from_s3,
        deleted_from_db=True
    )


@router.get("/list", response_model=ImageListResponse)
async def list_images(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of images to return")
):
    """
    List all images from database.
    
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of results (1-1000, default: 100)
    
    Returns:
        List of images with metadata
    """
    # Query images from database
    result = await db.execute(
        select(Image).offset(skip).limit(limit).order_by(Image.created_at.desc())
    )
    images = result.scalars().all()
    
    # Convert to list of ImageResponse
    image_responses = [ImageResponse.from_orm(img) for img in images]
    
    return ImageListResponse(
        count=len(image_responses),
        images=image_responses
    )


@router.get("/{image_id}/metadata", response_model=ImageResponse)
async def get_image_metadata(
    image_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get image metadata from database.
    
    - **image_id**: Unique image identifier
    
    Returns:
        Image metadata including S3 URL, file size, etc.
    """
    result = await db.execute(
        select(Image).where(Image.image_id == image_id)
    )
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return image


@router.get("/presigned-url/{image_id}", response_model=PresignedUrlResponse)
async def get_presigned_url(
    image_id: str,
    db: AsyncSession = Depends(get_db),
    expiration: int = Query(3600, ge=60, le=604800, description="URL expiration in seconds (60s - 7 days)")
):
    """
    Generate a presigned URL for temporary access to an image.
    
    - **image_id**: Unique image identifier
    - **expiration**: URL expiration time in seconds (default: 3600 = 1 hour)
    
    Returns:
        Presigned URL that expires after the specified time
    """
    # Get image metadata from database
    result = await db.execute(
        select(Image).where(Image.image_id == image_id)
    )
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found in database")
    
    presigned_url = await s3_service.generate_presigned_url(image.s3_key, expiration)
    
    return PresignedUrlResponse(
        image_id=image_id,
        presigned_url=presigned_url,
        expires_in=expiration
    )


@router.get("/check/{image_id}")
async def check_image_exists(
    image_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Check if an image exists in database and AWS S3.
    
    - **image_id**: Unique image identifier
    
    Returns:
        Existence status
    """
    # Check database
    result = await db.execute(
        select(Image).where(Image.image_id == image_id)
    )
    image = result.scalar_one_or_none()
    
    if not image:
        return {
            "image_id": image_id,
            "exists_in_db": False,
            "exists_in_s3": False,
            "message": "Image not found in database"
        }
    
    # Check S3
    exists_in_s3 = await s3_service.check_file_exists(image.s3_key)
    
    return {
        "image_id": image_id,
        "s3_key": image.s3_key,
        "exists_in_db": True,
        "exists_in_s3": exists_in_s3,
        "message": "Image found in both database and S3" if exists_in_s3 else "Image found in database but missing in S3"
    }


@router.get("/health")
async def images_health_check():
    """
    Health check endpoint for image service.
    
    Returns:
        Service status and configuration
    """
    from app.core.config import settings
    
    return {
        "status": "healthy",
        "service": "Image Service",
        "s3_bucket": settings.AWS_S3_BUCKET_NAME,
        "s3_region": settings.AWS_REGION,
        "max_file_size_mb": settings.AWS_S3_MAX_FILE_SIZE / (1024 * 1024),
        "allowed_extensions": settings.s3_allowed_extensions
    }

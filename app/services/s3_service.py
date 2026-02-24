"""
AWS S3 service for handling image uploads, downloads, and deletions.
"""
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import HTTPException, UploadFile
from app.core.config import settings
from typing import Optional, BinaryIO
import uuid
from datetime import datetime
import os
import base64
from io import BytesIO
from PIL import Image


class S3Service:
    """Service class for AWS S3 operations."""
    
    # Image size variants configuration
    IMAGE_VARIANTS = {
        'thumbnail': {'width': 150, 'height': 150, 'quality': 85},
        'small': {'width': 300, 'height': 300, 'quality': 85},
        'medium': {'width': 800, 'height': 800, 'quality': 90},
        'large': {'width': 1920, 'height': 1920, 'quality': 95},
    }
    
    def __init__(self):
        """Initialize S3 client with credentials from settings."""
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            self.bucket_name = settings.AWS_S3_BUCKET_NAME
            self.region = settings.AWS_REGION
        except NoCredentialsError:
            raise HTTPException(
                status_code=500,
                detail="AWS credentials not found. Please configure AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in .env file."
            )
    
    def _generate_image_id(self) -> str:
        """Generate unique image ID."""
        return f"img_{uuid.uuid4().hex[:16]}_{int(datetime.now().timestamp())}"
    
    def _get_file_extension(self, filename: str) -> str:
        """Extract file extension from filename."""
        return os.path.splitext(filename)[1].lower().lstrip('.')
    
    def _validate_file_extension(self, filename: str) -> bool:
        """Validate if file extension is allowed."""
        extension = self._get_file_extension(filename)
        allowed_extensions = settings.s3_allowed_extensions
        return extension in allowed_extensions
    
    def _validate_file_size(self, file_size: int) -> bool:
        """Validate if file size is within limits."""
        return file_size <= settings.AWS_S3_MAX_FILE_SIZE
    
    def _generate_s3_key(self, image_id: str, filename: str) -> str:
        """
        Generate S3 object key with organized folder structure.
        Format: images/YYYY/MM/DD/{image_id}_{filename}
        """
        now = datetime.now()
        date_path = now.strftime("%Y/%m/%d")
        return f"images/{date_path}/{image_id}_{filename}"
    
    def _get_s3_url(self, s3_key: str) -> str:
        """Generate public S3 URL for the uploaded object."""
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
    
    def _create_image_variant(self, image_bytes: bytes, max_width: int, max_height: int, quality: int) -> bytes:
        """
        Create a resized variant of the image.
        
        Args:
            image_bytes: Original image bytes
            max_width: Maximum width for the variant
            max_height: Maximum height for the variant
            quality: JPEG quality (1-100)
        
        Returns:
            bytes: Resized image bytes
        """
        img = Image.open(BytesIO(image_bytes))
        
        # Convert RGBA to RGB if needed
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Calculate new dimensions maintaining aspect ratio
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # Save to bytes
        output = BytesIO()
        img_format = 'JPEG' if img.format in (None, 'JPEG', 'JPG') else img.format
        img.save(output, format=img_format, quality=quality, optimize=True)
        return output.getvalue()
    
    def _upload_image_variants(self, image_bytes: bytes, base_s3_key: str, content_type: str, metadata: dict) -> dict:
        """
        Upload multiple quality variants of an image.
        
        Args:
            image_bytes: Original image bytes
            base_s3_key: Base S3 key (without extension)
            content_type: MIME type
            metadata: Metadata for S3 objects
        
        Returns:
            dict: URLs for all variants
        """
        variants = {}
        
        # Get file extension
        file_ext = base_s3_key.split('.')[-1] if '.' in base_s3_key else 'jpg'
        base_key_no_ext = '.'.join(base_s3_key.split('.')[:-1]) if '.' in base_s3_key else base_s3_key
        
        print(f"🔍 DEBUG: Creating variants for {base_s3_key}")
        print(f"🔍 DEBUG: File extension: {file_ext}, Base key: {base_key_no_ext}")
        
        try:
            # Upload original
            original_key = base_s3_key
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=original_key,
                Body=image_bytes,
                ContentType=content_type,
                Metadata=metadata
            )
            variants['original'] = self._get_s3_url(original_key)
            print(f"✅ Uploaded original: {variants['original']}")
            
            # Create and upload variants
            for variant_name, config in self.IMAGE_VARIANTS.items():
                variant_bytes = self._create_image_variant(
                    image_bytes,
                    config['width'],
                    config['height'],
                    config['quality']
                )
                
                variant_key = f"{base_key_no_ext}_{variant_name}.{file_ext}"
                
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=variant_key,
                    Body=variant_bytes,
                    ContentType=content_type,
                    Metadata={**metadata, 'variant': variant_name}
                )
                
                variants[variant_name] = self._get_s3_url(variant_key)
                print(f"✅ Uploaded {variant_name}: {variants[variant_name]}")
            
            print(f"🎉 All variants created: {list(variants.keys())}")
            return variants
            
        except Exception as e:
            print(f"❌ ERROR creating variants: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create image variants: {str(e)}"
            )
    
    async def upload_file(
        self,
        file: UploadFile,
        image_id: Optional[str] = None
    ) -> dict:
        """
        Upload file to S3 bucket.
        
        Args:
            file: FastAPI UploadFile object
            image_id: Optional custom image ID
        
        Returns:
            dict: Upload result with image details
        
        Raises:
            HTTPException: If upload fails or validation fails
        """
        # Validate file extension
        if not self._validate_file_extension(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed types: {', '.join(settings.s3_allowed_extensions)}"
            )
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Validate file size
        if not self._validate_file_size(file_size):
            max_size_mb = settings.AWS_S3_MAX_FILE_SIZE / (1024 * 1024)
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {max_size_mb}MB"
            )
        
        # Generate image ID and S3 key
        if not image_id:
            image_id = self._generate_image_id()
        s3_key = self._generate_s3_key(image_id, file.filename)
        
        # Upload to S3
        try:
            # Upload original and variants
            metadata = {
                'image_id': image_id,
                'original_filename': file.filename
            }
            
            variants = self._upload_image_variants(
                file_content,
                s3_key,
                file.content_type or 'image/jpeg',
                metadata
            )
            
            return {
                'image_id': image_id,
                'filename': file.filename,
                's3_key': s3_key,
                's3_url': variants['original'],
                'variants': variants,
                'file_size': file_size,
                'content_type': file.content_type
            }
        
        except ClientError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload image to S3: {str(e)}"
            )
    
    async def upload_base64(
        self,
        filename: str,
        base64_data: str,
        content_type: Optional[str] = None,
        image_id: Optional[str] = None
    ) -> dict:
        """
        Upload base64 encoded image to S3.
        
        Args:
            filename: Image filename
            base64_data: Base64 encoded image string
            content_type: MIME type
            image_id: Optional custom image ID
        
        Returns:
            dict: Upload result with image details
        
        Raises:
            HTTPException: If upload fails or validation fails
        """
        # Validate file extension
        if not self._validate_file_extension(filename):
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed types: {', '.join(settings.s3_allowed_extensions)}"
            )
        
        try:
            # Decode base64 data
            # Remove data URL prefix if present (e.g., "data:image/jpeg;base64,")
            if ',' in base64_data:
                base64_data = base64_data.split(',')[1]
            
            file_content = base64.b64decode(base64_data)
            file_size = len(file_content)
            
            # Validate file size
            if not self._validate_file_size(file_size):
                max_size_mb = settings.AWS_S3_MAX_FILE_SIZE / (1024 * 1024)
                raise HTTPException(
                    status_code=400,
                    detail=f"File size exceeds maximum allowed size of {max_size_mb}MB"
                )
            
            # Validate if it's actually an image
            try:
                img = Image.open(BytesIO(file_content))
                img.verify()
                
                # Determine content type if not provided
                if not content_type:
                    content_type = f"image/{img.format.lower()}" if img.format else "image/jpeg"
            except Exception:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid image data. Please provide a valid base64 encoded image."
                )
            
            # Generate image ID and S3 key
            if not image_id:
                image_id = self._generate_image_id()
            s3_key = self._generate_s3_key(image_id, filename)
            
            # Upload to S3 with variants
            metadata = {
                'image_id': image_id,
                'original_filename': filename
            }
            
            variants = self._upload_image_variants(
                file_content,
                s3_key,
                content_type,
                metadata
            )
            
            return {
                'image_id': image_id,
                'filename': filename,
                's3_key': s3_key,
                's3_url': variants['original'],
                'variants': variants,
                'file_size': file_size,
                'content_type': content_type
            }
        
        except base64.binascii.Error:
            raise HTTPException(
                status_code=400,
                detail="Invalid base64 data"
            )
        except ClientError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload image to S3: {str(e)}"
            )
    
    async def download_file(self, s3_key: str) -> tuple[bytes, str]:
        """
        Download file from S3.
        
        Args:
            s3_key: S3 object key
        
        Returns:
            tuple: (file_content, content_type)
        
        Raises:
            HTTPException: If download fails
        """
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            file_content = response['Body'].read()
            content_type = response['ContentType']
            
            return file_content, content_type
        
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise HTTPException(
                    status_code=404,
                    detail="Image not found in S3"
                )
            raise HTTPException(
                status_code=500,
                detail=f"Failed to download image from S3: {str(e)}"
            )
    
    async def delete_file(self, s3_key: str) -> bool:
        """
        Delete file from S3.
        
        Args:
            s3_key: S3 object key
        
        Returns:
            bool: True if deletion successful
        
        Raises:
            HTTPException: If deletion fails
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True
        
        except ClientError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete image from S3: {str(e)}"
            )
    
    async def list_files(self, prefix: str = "images/", max_keys: int = 100) -> list[dict]:
        """
        List files in S3 bucket.
        
        Args:
            prefix: S3 key prefix to filter results
            max_keys: Maximum number of results to return
        
        Returns:
            list: List of file metadata
        
        Raises:
            HTTPException: If listing fails
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            if 'Contents' not in response:
                return []
            
            files = []
            for obj in response['Contents']:
                files.append({
                    's3_key': obj['Key'],
                    's3_url': self._get_s3_url(obj['Key']),
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat()
                })
            
            return files
        
        except ClientError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to list images from S3: {str(e)}"
            )
    
    async def generate_presigned_url(
        self,
        s3_key: str,
        expiration: int = 3600
    ) -> str:
        """
        Generate presigned URL for temporary access to S3 object.
        
        Args:
            s3_key: S3 object key
            expiration: URL expiration time in seconds (default: 1 hour)
        
        Returns:
            str: Presigned URL
        
        Raises:
            HTTPException: If generation fails
        """
        try:
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            return presigned_url
        
        except ClientError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate presigned URL: {str(e)}"
            )
    
    async def check_file_exists(self, s3_key: str) -> bool:
        """
        Check if file exists in S3.
        
        Args:
            s3_key: S3 object key
        
        Returns:
            bool: True if file exists
        """
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True
        except ClientError:
            return False


# Global S3 service instance
s3_service = S3Service()

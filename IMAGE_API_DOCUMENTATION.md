# AWS S3 Image Storage API Documentation

## Overview
Complete REST API for managing image uploads, downloads, and storage using AWS S3. Supports both multipart file uploads and base64 encoded images.

---

## Configuration

### Environment Variables
Add these to your `.env` file:

```env
# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key_id_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key_here
AWS_REGION=eu-north-1
AWS_S3_BUCKET_NAME=sports-images-test
AWS_S3_MAX_FILE_SIZE=10485760  # 10MB
AWS_S3_ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,webp
```

### Prerequisites
- Python 3.8+
- AWS Account with S3 access
- S3 bucket created and configured
- IAM user with S3 permissions

---

## API Endpoints

### 1. Upload Image (Multipart)
Upload an image file using form-data.

**Endpoint:** `POST /images/upload`

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: 
  - `file`: Image file (jpg, jpeg, png, gif, webp)

**Response:**
```json
{
  "image_id": "img_a1b2c3d4e5f67890_1708531200",
  "filename": "profile-photo.jpg",
  "s3_key": "images/2026/02/20/img_a1b2c3d4e5f67890_1708531200_profile-photo.jpg",
  "s3_url": "https://sports-images-test.s3.eu-north-1.amazonaws.com/images/2026/02/20/img_a1b2c3d4e5f67890_1708531200_profile-photo.jpg",
  "file_size": 245678,
  "content_type": "image/jpeg",
  "message": "Image uploaded successfully to S3"
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/images/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/image.jpg"
```

**Python Example:**
```python
import requests

url = "http://localhost:8000/images/upload"
files = {"file": open("image.jpg", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

---

### 2. Upload Image (Base64)
Upload a base64 encoded image.

**Endpoint:** `POST /images/upload-base64`

**Request:**
- Method: `POST`
- Content-Type: `application/json`
- Body:
```json
{
  "filename": "profile.jpg",
  "base64_data": "/9j/4AAQSkZJRgABAQAAAQABAAD/...",
  "content_type": "image/jpeg"
}
```

**Response:**
```json
{
  "image_id": "img_a1b2c3d4e5f67890_1708531200",
  "filename": "profile.jpg",
  "s3_key": "images/2026/02/20/img_a1b2c3d4e5f67890_1708531200_profile.jpg",
  "s3_url": "https://sports-images-test.s3.eu-north-1.amazonaws.com/images/2026/02/20/img_a1b2c3d4e5f67890_1708531200_profile.jpg",
  "file_size": 245678,
  "content_type": "image/jpeg",
  "message": "Base64 image uploaded successfully to S3"
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/images/upload-base64" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "photo.jpg",
    "base64_data": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
    "content_type": "image/jpeg"
  }'
```

**JavaScript/TypeScript Example:**
```javascript
const base64Data = "data:image/jpeg;base64,/9j/4AAQSkZJRg...";

const response = await fetch("http://localhost:8000/images/upload-base64", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    filename: "photo.jpg",
    base64_data: base64Data,
    content_type: "image/jpeg"
  })
});

const result = await response.json();
console.log(result);
```

---

### 3. Download Image
Download an image from S3.

**Endpoint:** `GET /images/download/{image_id}`

**Parameters:**
- `image_id` (path): Unique image identifier
- `s3_key` (query): S3 object key

**Response:** Binary image data

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/images/download/img_abc123?s3_key=images/2026/02/20/img_abc123_photo.jpg" \
  --output downloaded-image.jpg
```

---

### 4. Delete Image
Delete an image from S3.

**Endpoint:** `DELETE /images/{image_id}`

**Parameters:**
- `image_id` (path): Unique image identifier
- `s3_key` (query): S3 object key to delete

**Response:**
```json
{
  "image_id": "img_a1b2c3d4e5f67890_1708531200",
  "message": "Image img_a1b2c3d4e5f67890_1708531200 deleted successfully from S3",
  "deleted_from_s3": true,
  "deleted_from_db": false
}
```

**cURL Example:**
```bash
curl -X DELETE "http://localhost:8000/images/img_abc123?s3_key=images/2026/02/20/img_abc123_photo.jpg"
```

---

### 5. List Images
List all images in S3 bucket.

**Endpoint:** `GET /images/list`

**Parameters:**
- `prefix` (query, optional): S3 key prefix filter (default: "images/")
- `max_results` (query, optional): Maximum results to return (1-1000, default: 100)

**Response:**
```json
{
  "count": 2,
  "images": [
    {
      "s3_key": "images/2026/02/20/img_abc123_photo1.jpg",
      "s3_url": "https://sports-images-test.s3.eu-north-1.amazonaws.com/images/2026/02/20/img_abc123_photo1.jpg",
      "size": 245678,
      "last_modified": "2026-02-20T10:30:00+00:00"
    },
    {
      "s3_key": "images/2026/02/20/img_def456_photo2.png",
      "s3_url": "https://sports-images-test.s3.eu-north-1.amazonaws.com/images/2026/02/20/img_def456_photo2.png",
      "size": 189234,
      "last_modified": "2026-02-20T11:15:00+00:00"
    }
  ]
}
```

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/images/list?prefix=images/&max_results=50"
```

---

### 6. Generate Presigned URL
Generate a temporary presigned URL for secure image access.

**Endpoint:** `GET /images/presigned-url/{image_id}`

**Parameters:**
- `image_id` (path): Unique image identifier
- `s3_key` (query): S3 object key
- `expiration` (query, optional): URL expiration in seconds (60-604800, default: 3600)

**Response:**
```json
{
  "image_id": "img_a1b2c3d4e5f67890_1708531200",
  "presigned_url": "https://sports-images-test.s3.eu-north-1.amazonaws.com/images/2026/02/20/img_abc123_photo.jpg?AWSAccessKeyId=...&Signature=...&Expires=...",
  "expires_in": 3600
}
```

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/images/presigned-url/img_abc123?s3_key=images/2026/02/20/img_abc123_photo.jpg&expiration=7200"
```

---

### 7. Check Image Exists
Check if an image exists in S3.

**Endpoint:** `GET /images/check/{image_id}`

**Parameters:**
- `image_id` (path): Unique image identifier
- `s3_key` (query): S3 object key to check

**Response:**
```json
{
  "image_id": "img_a1b2c3d4e5f67890_1708531200",
  "s3_key": "images/2026/02/20/img_abc123_photo.jpg",
  "exists": true,
  "message": "Image found in S3"
}
```

---

### 8. Health Check
Check image service health and configuration.

**Endpoint:** `GET /images/health`

**Response:**
```json
{
  "status": "healthy",
  "service": "Image Service",
  "s3_bucket": "sports-images-test",
  "s3_region": "eu-north-1",
  "max_file_size_mb": 10.0,
  "allowed_extensions": ["jpg", "jpeg", "png", "gif", "webp"]
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "File type not allowed. Allowed types: jpg, jpeg, png, gif, webp"
}
```

### 404 Not Found
```json
{
  "detail": "Image not found in S3"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to upload image to S3: [error details]"
}
```

---

## File Organization in S3

Images are organized in S3 with the following structure:
```
images/
  └── YYYY/
      └── MM/
          └── DD/
              └── {image_id}_{original_filename}
```

Example:
```
images/2026/02/20/img_a1b2c3d4e5f67890_1708531200_profile-photo.jpg
```

---

## Features

✅ **Multiple Upload Methods**: Supports both multipart file upload and base64 encoding  
✅ **Auto File Validation**: Validates file type and size  
✅ **Organized Storage**: Date-based folder structure in S3  
✅ **Unique IDs**: Generates unique identifiers for each image  
✅ **Presigned URLs**: Temporary secure access to images  
✅ **Direct Downloads**: Stream images directly from S3  
✅ **List & Search**: Browse all uploaded images  
✅ **Delete Support**: Remove images from S3  
✅ **Health Monitoring**: Service status endpoint  

---

## Testing

### Using Swagger UI
1. Start the server: `uvicorn app.main:app --reload`
2. Open browser: `http://localhost:8000/docs`
3. Try out the image endpoints interactively

### Using Python
```python
import requests
import base64

# Upload multipart file
with open("image.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/images/upload",
        files={"file": f}
    )
    result = response.json()
    print(f"Uploaded: {result['s3_url']}")

# Upload base64
with open("image.jpg", "rb") as f:
    base64_data = base64.b64encode(f.read()).decode()
    response = requests.post(
        "http://localhost:8000/images/upload-base64",
        json={
            "filename": "test.jpg",
            "base64_data": base64_data,
            "content_type": "image/jpeg"
        }
    )
    print(response.json())
```

---

## AWS S3 Bucket Setup

### 1. Create S3 Bucket
```bash
aws s3 mb s3://sports-images-test --region eu-north-1
```

### 2. Configure Bucket Policy (Optional - for public access)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::sports-images-test/*"
    }
  ]
}
```

### 3. Configure CORS (if accessing from browser)
```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
    "AllowedOrigins": ["*"],
    "ExposeHeaders": []
  }
]
```

### 4. Create IAM User with S3 Permissions
Required permissions:
- `s3:PutObject`
- `s3:GetObject`
- `s3:DeleteObject`
- `s3:ListBucket`

---

## Security Best Practices

1. **Never commit `.env` file** - Contains AWS credentials
2. **Use IAM roles** in production instead of access keys
3. **Enable S3 bucket encryption** for data at rest
4. **Set appropriate bucket policies** - Don't make entire bucket public unless needed
5. **Use presigned URLs** for temporary access instead of permanent public URLs
6. **Implement rate limiting** to prevent abuse
7. **Add authentication** to endpoints in production

---

## Troubleshooting

### AWS Credentials Not Found
```
Error: AWS credentials not found
Solution: Add AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY to .env file
```

### Bucket Not Found
```
Error: The specified bucket does not exist
Solution: Verify bucket name in AWS S3 console matches AWS_S3_BUCKET_NAME in .env
```

### Access Denied
```
Error: Access Denied
Solution: Check IAM user has proper S3 permissions (PutObject, GetObject, DeleteObject)
```

### File Too Large
```
Error: File size exceeds maximum allowed size
Solution: Adjust AWS_S3_MAX_FILE_SIZE in .env or reduce image size
```

---

## Next Steps

To add database storage for image metadata:
1. Enable `init_db()` in startup to create tables
2. Uncomment database operations in endpoints
3. Use the provided Image model to store metadata
4. Query database for faster image lookups

---

## Support

For issues or questions:
- Check logs: Look at terminal output for detailed error messages
- AWS Console: Verify S3 bucket exists and has correct permissions
- Test credentials: Use AWS CLI to verify credentials work
- Check IAM: Ensure IAM user has required S3 permissions

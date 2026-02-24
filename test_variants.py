"""Test script to check variants insertion"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://postgres:Admin@123@localhost:5432/sports_db_test1"

async def test_variants():
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        # Check if column exists
        result = await conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'images' AND column_name = 'variants';
        """))
        column_info = result.fetchone()
        print(f"\n✅ Column info: {column_info}")
        
        # Check latest image
        result = await conn.execute(text("""
            SELECT image_id, filename, variants, created_at 
            FROM images 
            ORDER BY created_at DESC 
            LIMIT 1;
        """))
        latest = result.fetchone()
        print(f"\n📸 Latest image: {latest}")
        
        # Try manual insert with variants
        test_variants = {
            "original": "https://test.com/original.jpg",
            "thumbnail": "https://test.com/thumb.jpg",
            "small": "https://test.com/small.jpg",
            "medium": "https://test.com/medium.jpg",
            "large": "https://test.com/large.jpg"
        }
        
        import json
        await conn.execute(text("""
            INSERT INTO images (image_id, filename, s3_key, s3_url, variants, file_size, content_type)
            VALUES ('test_img_123', 'test.jpg', 'test/test.jpg', 'https://test.com/test.jpg', :variants, 100, 'image/jpeg')
            ON CONFLICT (image_id) DO NOTHING;
        """), {"variants": json.dumps(test_variants)})
        
        print("\n✅ Test insert done!")
        
        # Check if it was inserted
        result = await conn.execute(text("""
            SELECT image_id, variants 
            FROM images 
            WHERE image_id = 'test_img_123';
        """))
        test_row = result.fetchone()
        print(f"\n🧪 Test row: {test_row}")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_variants())

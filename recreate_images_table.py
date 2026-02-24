"""
Script to drop and recreate the images table.
Run this when the table schema has changed.
"""
import asyncio
from app.core.database import engine, Base
from app.models import Image


async def recreate_images_table():
    """Drop and recreate the images table."""
    print("🔄 Dropping images table...")
    
    async with engine.begin() as conn:
        # Drop the images table
        await conn.run_sync(lambda sync_conn: 
            Base.metadata.tables['images'].drop(sync_conn, checkfirst=True)
        )
        print("✅ Images table dropped")
        
        # Recreate the images table
        await conn.run_sync(lambda sync_conn: 
            Base.metadata.tables['images'].create(sync_conn)
        )
        print("✅ Images table recreated with new schema")
    
    await engine.dispose()
    print("🎉 Done! You can now restart your server.")


if __name__ == "__main__":
    asyncio.run(recreate_images_table())

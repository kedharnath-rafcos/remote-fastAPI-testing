from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from contextlib import asynccontextmanager

from app.api.endpoints import users, images
from app.core.database import init_db, engine
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Async lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"🌍 Environment: {settings.ENVIRONMENT}")
    print(f"📊 Initializing database...")
    await init_db()
    print(f"✅ Application ready!")
    
    yield
    
    # Shutdown
    print("👋 Shutting down application...")
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Educational Sports Connect API with Async PostgreSQL Database",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(users.router)
app.include_router(images.router)


@app.get("/", tags=["Root"])
async def read_root():
    """Root endpoint - API welcome message."""
    return {
        "message": "Welcome to EduSportsConnect API",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.get("/db-test", tags=["Database"])
async def test_database_connection():
    """
    Test database connection and list all existing tables (async).
    
    Returns:
        - connection_status: Whether database is connected
        - database_info: Database name and host (anonymized)
        - tables: List of all tables in the database
        - table_count: Total number of tables
        - error: Error message if connection fails
    """
    try:
        # Test connection by executing a simple query
        async with engine.connect() as connection:
            result = await connection.execute(text("SELECT version();"))
            db_version = result.fetchone()[0]
        
        # Get database URL components
        db_name = engine.url.database
        db_host = engine.url.host
        db_port = engine.url.port
        
        # Get list of all tables using SQLAlchemy inspector
        async with engine.connect() as connection:
            tables = await connection.run_sync(
                lambda sync_conn: inspect(sync_conn).get_table_names()
            )
            
            # Get detailed table information
            table_details = []
            for table_name in tables:
                columns = await connection.run_sync(
                    lambda sync_conn: inspect(sync_conn).get_columns(table_name)
                )
                column_names = [col['name'] for col in columns]
                table_details.append({
                    "table_name": table_name,
                    "column_count": len(columns),
                    "columns": column_names
                })
        
        return {
            "connection_status": "✅ Connected (Async)",
            "database_info": {
                "host": db_host,
                "port": db_port,
                "database": db_name,
                "version": db_version.split(',')[0] if db_version else "Unknown",
                "driver": "asyncpg"
            },
            "tables": {
                "count": len(tables),
                "list": tables,
                "details": table_details
            },
            "message": "Database connection successful!" if tables else "Database connected but no tables found. Run the app to create tables automatically."
        }
        
    except Exception as e:
        # Return error details if connection fails
        raise HTTPException(
            status_code=503,
            detail={
                "connection_status": "❌ Failed",
                "error": str(e),
                "error_type": type(e).__name__,
                "message": "Could not connect to database. Please check your DATABASE_URL in .env file.",
                "troubleshooting": [
                    "1. Ensure PostgreSQL is running",
                    "2. Verify DATABASE_URL in .env file",
                    "3. Check database exists: CREATE DATABASE sports_db_test1;",
                    "4. Verify credentials are correct",
                    "5. Install asyncpg: pip install asyncpg"
                ]
            }
        )

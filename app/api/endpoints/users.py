"""
Users router with full async CRUD operations.
Demonstrates async PostgreSQL integration with FastAPI.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app import models, schemas


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/", response_model=List[schemas.UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all users from database (async).
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    result = await db.execute(
        select(models.User).offset(skip).limit(limit)
    )
    users = result.scalars().all()
    return users


@router.get("/{user_id}", response_model=schemas.UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a specific user by ID (async).
    
    - **user_id**: The ID of the user to retrieve
    """
    result = await db.execute(
        select(models.User).filter(models.User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return user


@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new user (async).
    
    - **name**: User's full name
    - **email**: User's email address (must be unique)
    """
    # Check if email already exists
    result = await db.execute(
        select(models.User).filter(models.User.email == user.email)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email {user.email} is already registered"
        )
    
    # Create new user
    db_user = models.User(**user.dict())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.put("/{user_id}", response_model=schemas.UserResponse)
async def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing user (async).
    
    - **user_id**: The ID of the user to update
    - **name**: Updated name (optional)
    - **email**: Updated email (optional)
    - **is_active**: Updated active status (optional)
    """
    result = await db.execute(
        select(models.User).filter(models.User.id == user_id)
    )
    db_user = result.scalar_one_or_none()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    # Check if email is being changed and if it already exists
    if user_update.email and user_update.email != db_user.email:
        result = await db.execute(
            select(models.User).filter(models.User.email == user_update.email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email {user_update.email} is already registered"
            )
    
    # Update user fields
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete a user (async).
    
    - **user_id**: The ID of the user to delete
    """
    result = await db.execute(
        select(models.User).filter(models.User.id == user_id)
    )
    db_user = result.scalar_one_or_none()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    await db.delete(db_user)
    await db.commit()
    return None


@router.get("/email/{email}", response_model=schemas.UserResponse)
async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a user by email address (async).
    
    - **email**: The email address to search for
    """
    result = await db.execute(
        select(models.User).filter(models.User.email == email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {email} not found"
        )
    return user

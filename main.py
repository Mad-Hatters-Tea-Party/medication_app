# main.py
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone
from models import User  # SQLAlchemy model
import models 
from schemas import UserCreate, UserUpdate, UserRead, UserDelete  # Pydantic models
from database import get_db  # Async database session
from passlib.context import CryptContext  # For password hashing and comparison


# Initialize FastAPI app
app = FastAPI()

# Initialize password hashing context (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") 


# Helper function to hash passwords
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Helper function to verify passwords
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Create a new user (POST)
@app.post("/users/", response_model=UserRead)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Hash the user's password before saving
    hashed_password = hash_password(user.user_pwd)
    print(f"User data: {user}")

    # Create a new user instance
    new_user = User(
        user_id=user.user_id,
        user_email=user.user_email,
        user_phone=user.user_phone,
        user_pwd=hashed_password,  # Store the hashed password
        user_gender=user.user_gender,
        user_dob=user.user_dob,
        user_height=user.user_height,
        user_weight=user.user_weight,
       created_at=datetime.now(timezone.utc),  # Set created_at to the current UTC time
        updated_at=datetime.now(timezone.utc)   # Set updated_at to the current UTC time
    )

     # Add and commit the new user to the database
    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)  # Refresh the instance with data from the DB
    except Exception as e:
        await db.rollback()  # Rollback in case of an error
        raise HTTPException(status_code=500, detail="Error creating user: " + str(e))

    return new_user


# Read a user by user_id (GET)
@app.get("/users/{user_id}", response_model=UserRead)
async def read_user(user_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.user_id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Update a user by user_id (PUT)
@app.put("/users/{user_id}", response_model=UserRead)
async def update_user(user_id: str, user_update: UserUpdate, db: AsyncSession = Depends(get_db)):
    # Query the user by user_id
    result = await db.execute(select(User).filter(User.user_id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

      # Update the user fields using model_dump()
    for field, value in user_update.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    # Set the updated_at field to the current UTC time
    user.updated_at = datetime.now(timezone.utc)

    try:
        await db.commit()  # Commit the transaction
        await db.refresh(user)  # Refresh the instance with updated data
    except Exception as e:
        await db.rollback()  # Rollback in case of an error
        raise HTTPException(status_code=500, detail="Error updating user: " + str(e))

    return user


# Delete user by user_id and password (DELETE)
@app.delete("/users/{user_id}", response_model=UserDelete)
async def delete_user(user_id: str, user_delete: UserDelete, db: AsyncSession = Depends(get_db)):
    # Fetch the user from the database using the user_id
    result = await db.execute(select(User).filter(User.user_id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if the password matches
    if not verify_password(user_delete.user_pwd, user.user_pwd):  # Hash comparison
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    # If password matches, delete the user
    try:
        await db.delete(user)
        await db.commit()  # Commit the transaction
    except Exception as e:
        await db.rollback()  # Rollback in case of an error
        raise HTTPException(status_code=500, detail="Error deleting user: " + str(e))

    return {"msg": "User deleted successfully", "user_id": user_id}



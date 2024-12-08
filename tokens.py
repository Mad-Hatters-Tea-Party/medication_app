from datetime import datetime, timedelta, timezone
from typing import Optional
from typing import Annotated
import secret_secrets as sec
from schemas import UserRead 
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel
from models import User  # Import your User model here
from database import get_db

SECRET_KEY = sec.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 60 minutes
REFRESH_TOKEN_EXPIRE_DAYS = 60     # Expiration time for refresh tokens 60 days 


# OAuth2PasswordBearer is a class that provides a standard way of getting the token from request headers
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# Initialize password hashing context (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") 

app = FastAPI()


# Helper function to hash passwords
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Helper function to verify passwords
# Helper function to verify passwords
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a hashed password using the configured password context.
    
    :param plain_password: The plain text password from the user input
    :param hashed_password: The hashed password from the database
    :return: True if passwords match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
# Function to refresh the token if it's expired
def refresh_access_token(user_id: str):
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_token = create_access_token(data={"sub": user_id}, expires_delta=expires_delta)
    return new_token

# Dependency to get current user, refresh token if expired
async def get_current_user_and_refresh_token(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if the token is expired
    expiration_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    if expiration_time < datetime.now(timezone.utc):  # Updated here
        # Token has expired, refresh it and return a new token
        new_token = refresh_access_token(user_id)
        return {"access_token": new_token, "token_type": "bearer"}
    # Token is still valid, return the original token
    return {"access_token": token, "token_type": "bearer"}

# Fetch the current user from the token
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> UserRead:
    try:
        payload = verify_token(token)
    except HTTPException as e:
        # If token is invalid or expired, return a custom error message asking to login again
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired or invalid. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    result = await db.execute(select(User).filter(User.user_id == user_id))
    user = result.scalars().first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return UserRead.model_validate(user) # pydantic v2 use model_validate() UserRead is pydantic model 

# Helper function to authenticate user credentials (username and password)
async def authenticate_user(db: AsyncSession, user_id: str, user_pwd: str) -> UserRead:
    result = await db.execute(select(User).filter(User.user_id == user_id))
    user = result.scalars().first()

    if user is None or not verify_password(user_pwd, user.user_pwd):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
      # Convert SQLAlchemy User to Pydantic UserRead model before returning
    return UserRead.model_validate(user)







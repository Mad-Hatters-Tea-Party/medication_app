
from typing import List
import logging
from sqlalchemy.exc import SQLAlchemyError
from fastapi import FastAPI, HTTPException, Depends, status, Response
from fastapi.responses import JSONResponse
from sqlalchemy import delete
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone
from models import User  # SQLAlchemy model for User
from models import Notification  # SQLAlchemy model for Notification
from models import Medication  # SQLAlchemy model for Medication
from models import Prescription # SQLAlchemy model for Prescription 
from models import PrescriptionDetail # SQLAlchemy model for PrescriptionDetail 
from models import SideEffect # SQLAlchemy model for Side Effect
import models 
from schemas import UserCreate, UserUpdate, UserRead, UserDelete, UserDeleteResponse, PasswordUpdateResponse, Token, UserResponse, UserLogin # Pydantic models
from schemas import SideEffectCreate, SideEffectRead, SideEffectUpdate, SideEffectDelete, SideEffectDeleteResponse
from schemas import NotificationCreate, NotificationUpdate, NotificationRead, NotificationDelete, NotificationDeleteResponse  # Pydantic schemas
from schemas import MedicationRead  # Pydantic schema for Medication
from schemas import PrescriptionCreate, PrescriptionUpdate, PrescriptionRead, PrescriptionDelete, PrescriptionDeleteResponse # Pydantic schemas for Prescription 
from schemas import PrescriptionDetailCreate, PrescriptionDetailUpdate, PrescriptionDetailRead, PrescriptionDetailDelete, PrescriptionDetailDeleteResponse# Pydantic schemas for PrescriptionDetail
from database import get_db  # Async database session
from passlib.context import CryptContext  # For password hashing and comparison
from tokens import *

# Configure logging
logging.basicConfig(level=logging.DEBUG)


# Initialize FastAPI app
#app = FastAPI()

'''# Initialize password hashing context (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") 


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
    return pwd_context.verify(plain_password, hashed_password)'''
#======================== User API Calls ===============================================
"""@app.post("/token/refresh")
async def refresh_access_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    # Verify the refresh token
    try:
        payload = verify_token(refresh_token)
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except HTTPException as e:
        raise e  # Propagate the exception if it's a verification failure

    # Fetch the user from the database using the user_id from the payload
    result = await db.execute(select(User).filter(User.user_id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create a new access token
    access_token = create_access_token(data={"sub": user_id})

    # Return the new access token
    return {"access_token": access_token, "token_type": "bearer"}"""

# Create a new user (POST) # register user 
@app.post("/register", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check if the user_id already exists in the database
    existing_user = await db.execute(select(User).filter(User.user_id == user.user_id))
    existing_user = existing_user.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail=f"User ID '{user.user_id}' is already taken. Please choose a different one."
        )

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

    # Return the user data along with the access token
    # Now that the user is created, we generate a JWT token
    access_token = create_access_token(data={"sub": new_user.user_id}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    # Return the user data along with the access token
     # Prepare the UserRead data
    user_data = UserRead.model_validate(new_user) # Convert from ORM model to Pydantic model
    
    # Prepare the response model (UserResponse)
    response = UserResponse(
        user=user_data,
        token_info=Token(access_token=access_token, token_type="bearer")
    )

    return response

# The login API
@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: UserLogin, db: AsyncSession = Depends(get_db)
):
    # Authenticate the user by checking user_id and user_pwd
    user = await authenticate_user(db, form_data.user_id, form_data.user_pwd)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Create an access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.user_id}, expires_delta=access_token_expires
    )
    
    # Return the token along with token type (bearer)
    return {"access_token": access_token, "token_type": "bearer"}


# Read current user 
@app.get("/users/me", response_model=UserResponse)
async def read_user(current_user: User = Depends(get_current_user), token_info: dict = Depends(get_current_user_and_refresh_token)):
    access_token = token_info['access_token']

    # Return the current user with the token info
    return UserResponse(
        user=UserRead.model_validate(current_user),  # Convert the SQLAlchemy user to the Pydantic UserRead model
        token_info=Token(access_token=access_token, token_type="bearer")
    )

# Update a user by user_id (PUT)
@app.put("/users/me")
async def update_user(
    user_update: UserUpdate, current_user: UserRead = Depends(get_current_user), db: AsyncSession = Depends(get_db)
    ):
    # The user_id is automatically derived from the current_user (token), no need to pass it in the path
    user_id = current_user.user_id

    # Query the user by user_id
    result = await db.execute(select(User).filter(User.user_id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if only password fields are passed (old and new passwords)
    if user_update.user_old_pwd and user_update.user_pwd:
        # Ensure the old password (current password) is provided for verification
        if not user_update.user_old_pwd:
            raise HTTPException(status_code=400, detail="Old password is required to update the password")

        # Verify the old password
        if not verify_password(user_update.user_old_pwd, user.user_pwd):
            raise HTTPException(status_code=401, detail="Old password is incorrect")

        # Hash the new password
        user_update.user_pwd = hash_password(user_update.user_pwd)

        # Update the user's password in the database
        user.user_pwd = user_update.user_pwd  # Update the password in the User model

        # Set the updated_at field to the current UTC time
        user.updated_at = datetime.now(timezone.utc)

        try:
            await db.commit()  # Commit the transaction
            await db.refresh(user)  # Refresh the instance with updated data
        except Exception as e:
            await db.rollback()  # Rollback in case of an error
            raise HTTPException(status_code=500, detail="Error updating user: " + str(e))

        # Return PasswordUpdateResponse with a success message
        return JSONResponse(
            content={"msg": "Password updated successfully", "user_id": user.user_id},
            status_code=status.HTTP_200_OK
        )

    # If password was not updated, update other fields
    for field, value in user_update.model_dump(exclude_unset=True).items():
        # Skip password-related fields
        if field not in ["user_old_pwd", "user_pwd"]:
            setattr(user, field, value)

    # Set the updated_at field to the current UTC time
    user.updated_at = datetime.now(timezone.utc)

    try:
        await db.commit()  # Commit the transaction
        await db.refresh(user)  # Refresh the instance with updated data
    except Exception as e:
        await db.rollback()  # Rollback in case of an error
        raise HTTPException(status_code=500, detail="Error updating user: " + str(e))

    # Return the updated user object (Pydantic model) - UserRead response
    return user  # This will use the UserRead response model for non-password updates

# Delete user by user_id and password (DELETE)
@app.delete("/users/me", response_model=UserDeleteResponse)
async def delete_user(
    user_delete: UserDelete, 
    current_user: UserRead = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    # Ensure the current user exists (this is essentially done by the get_current_user dependency)
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Fetch the user from the database using the user_id
    result = await db.execute(select(User).filter(User.user_id == current_user.user_id))
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

    # Return the success message with user_id
    return UserDeleteResponse(msg="User deleted successfully", user_id=user.user_id)
#======================== END User API Calls ===============================================
# ========================== Medication API calls ===============================================
# Get all medications (GET)
@app.get("/medications/", response_model=List[MedicationRead])
async def get_medications(db: AsyncSession = Depends(get_db)):
    # Query the database to get all medications
    result = await db.execute(select(Medication))  # No filtering, just select all medications
    medications = result.scalars().all()

    if not medications:
        raise HTTPException(status_code=404, detail="No medications found.")

    return medications  # FastAPI will automatically convert the list of Medication objects to MedicationRead
# ========================== End Medication API calls ===========================================

# =================== Notification API calls ==============================
# Create a new notification (POST)
@app.post("/notifications/", response_model=NotificationRead)
async def create_notification(
    notification: NotificationCreate, 
    current_user: User = Depends(get_current_user),  # Automatically get the user from the token
    db: AsyncSession = Depends(get_db)
):
    # Create a new notification instance with default values (None for optional fields)
    new_notification = Notification(
        user_id=current_user.user_id, # Use the user_id from the current authenticated user
        notification_type=notification.notification_type,  # Can be None
        notification_message=notification.notification_message,  # Can be None
        notification_date=notification.notification_date or datetime.now(timezone.utc),  # Set to current time if not provided
       # notification_status=notification.notification_status or None,  # Can be None
        created_at=datetime.now(timezone.utc),  # Set created_at to the current UTC time
        updated_at=datetime.now(timezone.utc)   # Set updated_at to the current UTC time
    )
  # Add and commit the new notification to the database
    db.add(new_notification)
    try:
        await db.commit()
        await db.refresh(new_notification)  # Refresh the instance with data from the DB
    except Exception as e:
        await db.rollback()  # Rollback in case of an error
        raise HTTPException(status_code=500, detail="Error creating notification: " + str(e))

    return new_notification

# Read a notification by notification_id (GET)
@app.get("/notifications/{notification_id}", response_model=NotificationRead)
async def read_notification(notification_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Fetch the notification by ID
    result = await db.execute(select(Notification).filter(Notification.notification_id == notification_id))
    notification = result.scalars().first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
     # Check if the notification belongs to the current user
    if notification.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this notification"
        )
    return notification

# Get all notifications for the current user (GET)
@app.get("/notifications", response_model=List[NotificationRead])
async def get_user_notifications(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Query the database to get notifications by current user's user_id
    result = await db.execute(select(Notification).filter(Notification.user_id == current_user.user_id))
    notifications = result.scalars().all()

    if not notifications:
        raise HTTPException(status_code=404, detail="No notifications found for the user.")

    return notifications  # FastAPI will handle serialization to NotificationRead

# Update a notification by notification_id (PUT)
@app.put("/notifications/{notification_id}", response_model=NotificationRead)
async def update_notification(notification_id: int, notification_update: NotificationUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Query the notification by notification_id
    result = await db.execute(select(Notification).filter(Notification.notification_id == notification_id))
    notification = result.scalars().first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    # Check if the notification belongs to the current user
    if notification.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this notification"
        )
     # Update the notification fields using model_dump()
    for field, value in notification_update.model_dump(exclude_unset=True).items():
        setattr(notification, field, value)

    # Set the updated_at field to the current UTC time
    notification.updated_at = datetime.now(timezone.utc)

    try:
        await db.commit()  # Commit the transaction
        await db.refresh(notification)  # Refresh the instance with updated data
    except Exception as e:
        await db.rollback()  # Rollback in case of an error
        raise HTTPException(status_code=500, detail="Error updating notification: " + str(e))

    return notification

# Delete notification by notification_id (DELETE)
async def delete_notification(notification_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Query the notification by notification_id
    result = await db.execute(select(Notification).filter(Notification.notification_id == notification_id))
    notification = result.scalars().first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
     # Check if the notification belongs to the current user
    if notification.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this notification"
        )

    try:
        await db.delete(notification)  # Delete the notification instance
        await db.commit()  # Commit the transaction
    except Exception as e:
        await db.rollback()  # Rollback in case of an error
        raise HTTPException(status_code=500, detail="Error deleting notification: " + str(e))

    return {"msg": "Notification deleted successfully", "notification_id": notification_id}

# ================ END of Notification API Calls ======================================================================
# ======================== Percription API Calls ======================================================================
@app.post("/prescriptions/", response_model=PrescriptionRead)
async def create_prescription(prescription: PrescriptionCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Create a new Prescription instance
    new_prescription = Prescription(
        user_id=current_user.user_id,
        prescription_date_start=prescription.prescription_date_start,
        prescription_date_end=prescription.prescription_date_end,
        prescription_status=prescription.prescription_status,
    )
      # Add the new prescription to the database
    db.add(new_prescription)
    try:
        await db.commit()
        await db.refresh(new_prescription)  # Refresh the instance with data from the DB
    except Exception as e:
        await db.rollback()  # Rollback in case of an error
        raise HTTPException(status_code=500, detail=f"Error creating prescription: {str(e)}")

    return new_prescription

# read prescription by prescription id 
@app.get("/prescriptions/{prescription_id}", response_model=PrescriptionRead)
async def get_prescription(prescription_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Prescription)
        .options(
            selectinload(Prescription.prescription_details)
            .selectinload(PrescriptionDetail.medication)  # Eager load medication
        )
        .filter(Prescription.prescription_id == prescription_id)
    )
    prescription = result.scalars().first()

    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
     # Check if the prescription belongs to the current user
    if prescription.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access this prescription"
        )

    # Convert the Prescription model to the PrescriptionRead Pydantic model
    prescription_data = []
    for detail in prescription.prescription_details:
        # Create PrescriptionDetailRead and include medication_name
        prescription_data.append(PrescriptionDetailRead(
            prescription_id=detail.prescription_id,
            medication_id=detail.medication_id,
            medication_name=detail.medication.medication_name,  # Fetch medication_name
            presc_dose=detail.presc_dose,
            presc_qty=detail.presc_qty,
            presc_type=detail.presc_type,
            presc_frequency=detail.presc_frequency
        ))

    # Return PrescriptionRead including details and medication name
    return PrescriptionRead(
        prescription_id=prescription.prescription_id,
        prescription_date_start=prescription.prescription_date_start,
        prescription_date_end=prescription.prescription_date_end,
        prescription_status=prescription.prescription_status,
        user_id=prescription.user_id,
        prescription_details=prescription_data
    )
# read full list of prescriptions associated with user_id (user_id from token)
@app.get("/prescriptions/", response_model=List[PrescriptionRead])
async def get_prescriptions_by_user(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Prescription)
        .options(
            selectinload(Prescription.prescription_details)
            .selectinload(PrescriptionDetail.medication)  # Eager load medication
        )
        .filter(Prescription.user_id == current_user.user_id)  # Filter by user_id
    )
    prescriptions = result.scalars().all()  # Get all prescriptions for the user

    if not prescriptions:
        raise HTTPException(status_code=404, detail="No prescriptions found for this user")

    # Convert the list of Prescription models to PrescriptionRead Pydantic models
    prescriptions_data = []
    for prescription in prescriptions:
        prescription_data = []
        for detail in prescription.prescription_details:
            prescription_data.append(PrescriptionDetailRead(
                prescription_id=detail.prescription_id,
                medication_id=detail.medication_id,
                medication_name=detail.medication.medication_name,  # Medication name
                presc_dose=detail.presc_dose,
                presc_qty=detail.presc_qty,
                presc_type=detail.presc_type,
                presc_frequency=detail.presc_frequency
            ))

        prescriptions_data.append(PrescriptionRead(
            prescription_id=prescription.prescription_id,
            prescription_date_start=prescription.prescription_date_start,
            prescription_date_end=prescription.prescription_date_end,
            prescription_status=prescription.prescription_status,
            user_id=prescription.user_id,
            prescription_details=prescription_data
        ))

    # Return the list of PrescriptionRead models for the user
    return prescriptions_data


# update precription by prescription_id 
@app.put("/prescriptions/{prescription_id}", response_model=PrescriptionRead)
async def update_prescription(prescription_id: int, prescription_update: PrescriptionUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Query the prescription by prescription_id
    result = await db.execute(select(Prescription).filter(Prescription.prescription_id == prescription_id))
    prescription = result.scalars().first()

    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
     # Check if the prescription belongs to the current user
    if prescription.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access this prescription"
        )


    # Update the prescription fields using the provided data
    for field, value in prescription_update.model_dump(exclude_unset=True).items():
        setattr(prescription, field, value)

    try:
        await db.commit()
        await db.refresh(prescription)  # Refresh the instance with updated data
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating prescription: {str(e)}")

    return prescription

# delete percription by prescription_id 
@app.delete("/prescriptions/{prescription_id}", response_model=PrescriptionDeleteResponse)
async def delete_prescription(prescription_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Fetch the prescription from the database using the prescription_id
    result = await db.execute(select(Prescription).filter(Prescription.prescription_id == prescription_id))
    prescription = result.scalars().first()

    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    
    # Check if the prescription belongs to the current user
    if prescription.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this prescription")

    try:
        await db.delete(prescription)
        await db.commit()  # Commit the transaction
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting prescription: {str(e)}")

    return {"msg": "Prescription deleted successfully", "prescription_id": prescription_id}

#================================= END Prescription API calls ========================================================

# ================================ PrescriptionDetail API calls ================================================

# create PrescriptionDetail 
@app.post("/prescriptions/{prescription_id}/details/", response_model=PrescriptionDetailRead)
async def create_prescription_detail(
    prescription_id: int, 
    detail: PrescriptionDetailCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if the prescription exists in the database
    prescription = await db.execute(select(Prescription).filter(Prescription.prescription_id == prescription_id))
    prescription = prescription.scalars().first()
    if not prescription:
        raise HTTPException(
            status_code=404,
            detail=f"Prescription with id {prescription_id} not found."
        )
     # Check if the prescription belongs to the current user
    if prescription.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access this prescription"
        )

    # Check if the medication exists in the database
    medication = await db.execute(select(Medication).filter(Medication.medication_id == detail.medication_id))
    medication = medication.scalars().first()
    if not medication:
        raise HTTPException(
            status_code=404,
            detail=f"Medication with id {detail.medication_id} not found."
        )

    # Create a new PrescriptionDetail instance
    new_detail = PrescriptionDetail(
        prescription_id=prescription_id,
        medication_id=detail.medication_id,
        presc_dose=detail.presc_dose,
        presc_qty=detail.presc_qty,
        presc_type=detail.presc_type,
        presc_frequency=detail.presc_frequency
    )

    # Add the new detail to the database
    db.add(new_detail)
    try:
        await db.commit()
        await db.refresh(new_detail)  # Refresh the instance with data from the DB
    except Exception as e:
        await db.rollback()  # Rollback in case of an error
        raise HTTPException(status_code=500, detail=f"Error creating prescription detail: {str(e)}")

    return new_detail


# Get all Prescription Details by Prescription ID 
@app.get("/prescriptions/{prescription_id}/details/", response_model=List[PrescriptionDetailRead])
async def get_prescription_details(prescription_id: int, db: AsyncSession = Depends(get_db),  current_user: User = Depends(get_current_user)):
    # Query to fetch the prescription by prescription_id
    result = await db.execute(
        select(Prescription)
        .filter(Prescription.prescription_id == prescription_id)
    )
    prescription = result.scalars().first()

    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    # Check if the prescription belongs to the current user
    if prescription.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to view this prescription")

    # Query to fetch prescription details along with medication name
    newresult = await db.execute(
        select(PrescriptionDetail, Medication.medication_name)  # Select both prescription details and medication name
        .join(Medication, Medication.medication_id == PrescriptionDetail.medication_id)  # Join with Medication model
        .filter(PrescriptionDetail.prescription_id == prescription_id)
    )
    
    # Fetch all results
    details = newresult.all()

    if not details:
        raise HTTPException(status_code=404, detail="Prescription details not found")

    # Convert the result to the response model
    prescription_details = []
    for detail, medication_name in details:
        # Convert each detail row into PrescriptionDetailRead, adding the medication_name
        prescription_details.append(PrescriptionDetailRead(
            prescription_id=detail.prescription_id,
            medication_id=detail.medication_id,
            medication_name=medication_name,  # Add the fetched medication name
            presc_dose=detail.presc_dose,
            presc_qty=detail.presc_qty,
            presc_type=detail.presc_type,
            presc_frequency=detail.presc_frequency
        ))

    return prescription_details

# update the details of an existing prescription detail
@app.put("/prescriptions/{prescription_id}/details/{medication_id}", response_model=PrescriptionDetailRead)
async def update_prescription_detail(
    prescription_id: int,
    medication_id: int,
    detail_update: PrescriptionDetailUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserRead = Depends(get_current_user) 
):
    # Check if the prescription exists in the database
    prescription = await db.execute(select(Prescription).filter(Prescription.prescription_id == prescription_id))
    prescription = prescription.scalars().first()
    if not prescription:
        raise HTTPException(
            status_code=404,
            detail=f"Prescription with id {prescription_id} not found."
        )
    
     # Check if the prescription belongs to the current user
    if prescription.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to update this prescription")

    # Check if the medication exists in the database
    medication = await db.execute(select(Medication).filter(Medication.medication_id == medication_id))
    medication = medication.scalars().first()
    if not medication:
        raise HTTPException(
            status_code=404,
            detail=f"Medication with id {medication_id} not found."
        )

    # Query the existing prescription detail by prescription_id and medication_id
    result = await db.execute(select(PrescriptionDetail).filter(
        PrescriptionDetail.prescription_id == prescription_id,
        PrescriptionDetail.medication_id == medication_id
    ))
    detail = result.scalars().first()

    if not detail:
        raise HTTPException(status_code=404, detail="Prescription detail not found")

    # Update the detail fields using the provided data
    for field, value in detail_update.model_dump(exclude_unset=True).items():
        setattr(detail, field, value)

    # Convert SQLAlchemy model to Pydantic model using model_validate
    # The 'medication_name' will be set manually below
    detail_pydantic = PrescriptionDetailRead.model_validate(detail)  # This replaces from_orm

    # Set medication_name explicitly
    detail_pydantic.medication_name = medication.medication_name

    try:
        await db.commit()
        await db.refresh(detail)  # Refresh the instance with updated data
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating prescription detail: {str(e)}")

    # Return the updated detail with medication_name
    return detail_pydantic  # Return the Pydantic model with medication_name field included



# deletes a prescription detail based on both prescription_id and medication_id
@app.delete("/prescriptions/{prescription_id}/details/{medication_id}", response_model=PrescriptionDetailDeleteResponse)
async def delete_prescription_detail(prescription_id: int, medication_id: int, db: AsyncSession = Depends(get_db), current_user: UserRead = Depends(get_current_user)):
    # Fetch the prescription from the database using prescription_id
    result = await db.execute(select(Prescription).filter(Prescription.prescription_id == prescription_id))
    prescription = result.scalars().first()

    #check is prescription exists 
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    # Check if the prescription belongs to the current user
    if prescription.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this prescription")

    # Fetch the prescription detail using prescription_id and medication_id
    result = await db.execute(select(PrescriptionDetail).filter(
        PrescriptionDetail.prescription_id == prescription_id,
        PrescriptionDetail.medication_id == medication_id
    ))
    detail = result.scalars().first()

    if not detail:
        raise HTTPException(status_code=404, detail="Prescription detail not found")

    try:
        await db.delete(detail)
        await db.commit()  # Commit the transaction
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting prescription detail: {str(e)}")

    return {"msg": "Prescription detail deleted successfully", "prescription_id": prescription_id, "medication_id": medication_id}

# ============================== END Prescription detail API calls =================================================================

#================================== Side effects API calls ====================================================

class DataAccessOperations:
    def __init__(self):
        # No need for self.db anymore, the db session will be passed explicitly.
        pass

    async def insert_side_effect(self, db: AsyncSession, incoming_side_effect: SideEffectCreate, user_id: str, ):
        # Check if the user exists
        """user = await db.execute(select(User).filter_by(user_id=incoming_side_effect.user_id))
        user = user.scalar_one_or_none()  # Get the user if it exists, or None if not

        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User with user_id {incoming_side_effect.user_id} not found."
            )"""

        # Check if the medication exists
        medication = await db.execute(select(Medication).filter_by(medication_id=incoming_side_effect.medication_id))
        medication = medication.scalar_one_or_none()

        if not medication:
            raise HTTPException(
                status_code=404,
                detail=f"Medication with medication_id {incoming_side_effect.medication_id} not found."
            )

        # Proceed with insertion if both user and medication exist
        # Set created_at and updated_at to the current UTC time
        current_time = datetime.now(timezone.utc)
        data_to_insert = SideEffect(**incoming_side_effect.model_dump(), created_at=current_time, updated_at=current_time, user_id=user_id)

        # Insert the side effect into the database
        db.add(data_to_insert)
        await db.commit()
        await db.refresh(data_to_insert)  # Refresh to get the inserted data

        # Fetch the medication name by joining the Medication table with the inserted SideEffect
        query = select(SideEffect, Medication.medication_name).join(
            Medication, Medication.medication_id == SideEffect.medication_id
        ).where(SideEffect.side_effects_id == data_to_insert.side_effects_id)

        result = await db.execute(query)
        side_effect_with_med_name = result.all()

        if not side_effect_with_med_name:
            raise HTTPException(
                status_code=404,
                detail=f"Side effect with id {data_to_insert.side_effects_id} not found."
            )
        # Unpack the first (and only) tuple from the result
        side_effect, medication_name = side_effect_with_med_name[0]

        # Return the response with medication_name included
        side_effect_with_med_nameresponse = SideEffectRead(
            side_effects_id=side_effect.side_effects_id,
            user_id=side_effect.user_id,
            medication_id=side_effect.medication_id,
            medication_name=medication_name,  # Include medication_name in the response
            side_effect_desc=side_effect.side_effect_desc,
            created_at=side_effect.created_at,
            updated_at=side_effect.updated_at
        )

        return DataAccessOperations.DataAccessResult(success=True, result_data=[side_effect_with_med_nameresponse])




    async def read_side_effects_for_user(self, db: AsyncSession, user_id: str):
        try:
            # Join the SideEffect table with Medication to fetch medication_name
            query = select(SideEffect, Medication.medication_name).join(
            Medication, Medication.medication_id == SideEffect.medication_id
            ).where(SideEffect.user_id == user_id)

            # Execute the query
            result = await db.execute(query)

            # Collect the results
            side_effects_with_med_name = []
            for side_effect, medication_name in result.all():
                side_effect_data = SideEffectRead(
                    side_effects_id=side_effect.side_effects_id,
                    user_id=side_effect.user_id,
                    medication_id=side_effect.medication_id,
                    medication_name=medication_name,  # Add medication_name to the response
                    side_effect_desc=side_effect.side_effect_desc,
                    created_at=side_effect.created_at,
                    updated_at=side_effect.updated_at
                )
                side_effects_with_med_name.append(side_effect_data)

            return DataAccessOperations.DataAccessResult(success=True, result_data=side_effects_with_med_name)

        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail="An error occurred while querying the database for side effects."
            )

    async def read_side_effects_for_medication_and_user(self, db: AsyncSession, medication_id: str, user_id: str):
        # Query side effects for the specified medication and user, including medication name
        try:
            # Join SideEffect with Medication to fetch medication_name
            query = select(SideEffect, Medication.medication_name).join(
                Medication, Medication.medication_id == SideEffect.medication_id
            ).where(
                SideEffect.medication_id == medication_id,
                SideEffect.user_id == user_id
            )

            # Execute the query
            result = await db.execute(query)

            # Collect the results
            side_effects_with_med_name = []
            for side_effect, medication_name in result.all():
                side_effect_data = SideEffectRead(
                    side_effects_id=side_effect.side_effects_id,
                    user_id=side_effect.user_id,
                    medication_id=side_effect.medication_id,
                    medication_name=medication_name,  # Adding the medication name to the result
                    side_effect_desc=side_effect.side_effect_desc,
                    created_at=side_effect.created_at,
                    updated_at=side_effect.updated_at
                )
                side_effects_with_med_name.append(side_effect_data)

            return DataAccessOperations.DataAccessResult(success=True, result_data=side_effects_with_med_name)
        
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail="An error occurred while querying the database for side effects."
            )

    async def delete_side_effect(self, db: AsyncSession, side_effects_id: int):
        return await self.delete_from_db(db, delete(SideEffect).where(SideEffect.side_effects_id == side_effects_id))

    async def query_db(self, db: AsyncSession, query: any):
        try:
            result = await db.execute(query)
            return DataAccessOperations.DataAccessResult(success=True, result_data=result.scalars().all())
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail="An error occurred while querying the database."
            )

    async def delete_from_db(self, db: AsyncSession, query: any):
        try:
            result = await db.execute(query)
            await db.commit()
            if result.rowcount > 0:
                return DataAccessOperations.DataAccessResult(success=True, result_data=None)
            else:
                return DataAccessOperations.DataAccessResult(success=False, result_data=None)
        except SQLAlchemyError as e:
            await db.rollback()  # Rollback in case of an error
            raise HTTPException(
                status_code=500,
                detail="An error occurred while deleting the side effect."
            )

    # POPO representing the result of data access operations
    class DataAccessResult:
        def __init__(self, success: bool, result_data: List = None):
            self.success = success
            self.result_data = result_data or []


data_access_operations = DataAccessOperations()



# Create Side Effect
@app.post("/side_effects/", response_model=SideEffectRead)
async def create_side_effect(data_to_insert: SideEffectCreate, db: AsyncSession = Depends(get_db), current_user: UserRead = Depends(get_current_user)):
   # Ensure the user matches the current user from the token
    #data_to_insert.user_id = current_user.user_id  # Ensure the current user's ID is used

    result = await data_access_operations.insert_side_effect(db=db, incoming_side_effect=data_to_insert, user_id=current_user.user_id)

    if not result.success:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to insert side effect for user: {current_user.user_id}"
        )

    return result.result_data[0]

#read all side Effects for current user
@app.get("/side_effects/", response_model=List[SideEffectRead])
async def read_side_effect_for_user(db: AsyncSession = Depends(get_db), current_user: UserRead = Depends(get_current_user)):

    # Query the side effects for the user, now including the medication name
    result = await data_access_operations.read_side_effects_for_user(db=db, user_id=current_user.user_id)

    # If the result is not successful, raise an error
    if not result.success:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to retrieve side effects for user: {current_user.user_id}"
        )

    # Return the list of side effects, which now includes medication names
    return result.result_data


# Read all Side Effects for a Medication for current User with Medication Name
@app.get("/side_effects/medication/{medication_id}/user/", response_model=List[SideEffectRead])
async def read_side_effect_for_medication_and_user(medication_id: str, db: AsyncSession = Depends(get_db), current_user: UserRead = Depends(get_current_user)):
    # Validate the medication_id and user_id inputs
    if not medication_id or not medication_id.strip():
        raise HTTPException(
            status_code=422,
            detail="Incoming medication id is malformed"
        )

    # Query the side effects for the specified medication and user along with the medication name
    result = await data_access_operations.read_side_effects_for_medication_and_user(db=db, medication_id=medication_id, user_id=current_user.user_id)

    # If the result is not successful, raise an error
    if not result.success:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to retrieve side effects for medication id: {medication_id} and user id: {current_user.user_id}"
        )

    # Return the list of side effects
    return result.result_data

# Delete Side Effect
# Delete Side Effect
@app.delete("/side_effects/{side_effects_id}", response_model=SideEffectDeleteResponse)
async def delete_side_effect(side_effects_id: int, db: AsyncSession = Depends(get_db), current_user: UserRead = Depends(get_current_user)):
    # Fetch the side effect from the database
    result = await db.execute(select(SideEffect).filter(SideEffect.side_effects_id == side_effects_id))
    side_effect = result.scalars().first()

    if not side_effect:
        raise HTTPException(status_code=404, detail="Side effect not found")

    # Check if the side effect belongs to the current user
    if side_effect.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this side effect")

    result = await data_access_operations.delete_side_effect(db=db, side_effects_id=side_effects_id)

    if result.success:
        return SideEffectDeleteResponse(msg="Side effect successfully deleted.", side_effects_id=side_effects_id)
    else:
        return SideEffectDeleteResponse(msg="Failed to delete side effect.", side_effects_id=None)


# Update Side Effect
@app.put("/side_effects/{side_effects_id}", response_model=SideEffectRead)
async def side_effects_update(side_effects_id: int, update_data: SideEffectUpdate, db: AsyncSession = Depends(get_db), current_user: UserRead = Depends(get_current_user)):
    # Fetch the side effect from the database
    side_effect = await db.execute(select(SideEffect).where(SideEffect.side_effects_id == side_effects_id))
    side_effect = side_effect.scalar_one_or_none()
    # check if side effect exists 
    if not side_effect:
        raise HTTPException(
            status_code=404,
            detail=f"Side effect with id {side_effects_id} not found."
        )
    
    # Check if the side effect belongs to the current user
    if side_effect.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to update this side effect")


    # Update the side effect description if provided
    if update_data.side_effect_desc:
        side_effect.side_effect_desc = update_data.side_effect_desc

    # Update the updated_at field to current UTC time
    side_effect.updated_at = datetime.now(timezone.utc)

    try:
        # Commit the changes
        await db.commit()
        await db.refresh(side_effect)  # Refresh to get updated data from database

        # Return the updated side effect
        return side_effect  # This will be serialized via the SideEffectRead model

    except SQLAlchemyError as e:
        # Rollback in case of an error
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="An error occurred while updating the side effect."
        )
    

















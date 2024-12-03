# main.py
from typing import List
from fastapi import FastAPI, HTTPException, Depends
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
import models 
from schemas import UserCreate, UserUpdate, UserRead, UserDelete, UserDeleteResponse  # Pydantic models
from schemas import NotificationCreate, NotificationUpdate, NotificationRead, NotificationDelete, NotificationDeleteResponse  # Pydantic schemas
from schemas import MedicationRead  # Pydantic schema for Medication
from schemas import PrescriptionCreate, PrescriptionUpdate, PrescriptionRead, PrescriptionDelete, PrescriptionDeleteResponse # Pydantic schemas for Prescription 
from schemas import PrescriptionDetailCreate, PrescriptionDetailUpdate, PrescriptionDetailRead, PrescriptionDetailDelete, PrescriptionDetailDeleteResponse# Pydantic schemas for PrescriptionDetail
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
# Helper function to verify passwords
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a hashed password using the configured password context.
    
    :param plain_password: The plain text password from the user input
    :param hashed_password: The hashed password from the database
    :return: True if passwords match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)
#======================== User API Calls ===============================================
# Create a new user (POST)
@app.post("/users/", response_model=UserRead)
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

    # Check if user is attempting to update the password
    if user_update.user_pwd:
        # Ensure the old password (current password) is provided for verification
        if not user_update.user_old_pwd:
            raise HTTPException(status_code=400, detail="Old password is required to update the password")

        # Verify the old password
        if not verify_password(user_update.user_old_pwd, user.user_pwd):
            raise HTTPException(status_code=401, detail="Old password is incorrect")

        # Hash the new password
        user_update.user_pwd = hash_password(user_update.user_pwd)
    
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
@app.delete("/users/{user_id}", response_model=UserDeleteResponse)
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

    # Return the success message with user_id
    return UserDeleteResponse(msg="User deleted successfully", user_id=user_id)
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
async def create_notification(notification: NotificationCreate, db: AsyncSession = Depends(get_db)):
    # Create a new notification instance with default values (None for optional fields)
    new_notification = Notification(
        user_id=notification.user_id,
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
async def read_notification(notification_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Notification).filter(Notification.notification_id == notification_id))
    notification = result.scalars().first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

# Get all notifications for a user id (GET)
@app.get("/notifications/user/{user_id}", response_model=List[NotificationRead])
async def get_user_notifications(user_id: str, db: AsyncSession = Depends(get_db)):
    # Query the database to get notifications by user_id
    result = await db.execute(select(Notification).filter(Notification.user_id == user_id))
    notifications = result.scalars().all()

    if not notifications:
        raise HTTPException(status_code=404, detail="No notifications found for the user.")

    return notifications  # FastAPI will handle serialization to NotificationRead

# Update a notification by notification_id (PUT)
@app.put("/notifications/{notification_id}", response_model=NotificationRead)
async def update_notification(notification_id: int, notification_update: NotificationUpdate, db: AsyncSession = Depends(get_db)):
    # Query the notification by notification_id
    result = await db.execute(select(Notification).filter(Notification.notification_id == notification_id))
    notification = result.scalars().first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
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
@app.delete("/notifications/{notification_id}", response_model=NotificationDeleteResponse)
async def delete_notification(notification_id: int, db: AsyncSession = Depends(get_db)):
    # Query the notification by notification_id
    result = await db.execute(select(Notification).filter(Notification.notification_id == notification_id))
    notification = result.scalars().first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

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
async def create_prescription(prescription: PrescriptionCreate, db: AsyncSession = Depends(get_db)):
    # Create a new Prescription instance
    new_prescription = Prescription(
        user_id=prescription.user_id,
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


@app.get("/prescriptions/{prescription_id}", response_model=PrescriptionRead)
async def get_prescription(prescription_id: int, db: AsyncSession = Depends(get_db)):
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

# update precription by prescription_id 
@app.put("/prescriptions/{prescription_id}", response_model=PrescriptionRead)
async def update_prescription(prescription_id: int, prescription_update: PrescriptionUpdate, db: AsyncSession = Depends(get_db)):
    # Query the prescription by prescription_id
    result = await db.execute(select(Prescription).filter(Prescription.prescription_id == prescription_id))
    prescription = result.scalars().first()

    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

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
async def delete_prescription(prescription_id: int, db: AsyncSession = Depends(get_db)):
    # Fetch the prescription from the database using the prescription_id
    result = await db.execute(select(Prescription).filter(Prescription.prescription_id == prescription_id))
    prescription = result.scalars().first()

    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

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
    db: AsyncSession = Depends(get_db)
):
    # Check if the prescription exists in the database
    prescription = await db.execute(select(Prescription).filter(Prescription.prescription_id == prescription_id))
    prescription = prescription.scalars().first()
    if not prescription:
        raise HTTPException(
            status_code=404,
            detail=f"Prescription with id {prescription_id} not found."
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
async def get_prescription_details(prescription_id: int, db: AsyncSession = Depends(get_db)):
    # Query to fetch prescription details along with medication name
    result = await db.execute(
        select(PrescriptionDetail, Medication.medication_name)  # Select both prescription details and medication name
        .join(Medication, Medication.medication_id == PrescriptionDetail.medication_id)  # Join with Medication model
        .filter(PrescriptionDetail.prescription_id == prescription_id)
    )
    
    # Fetch all results
    details = result.all()

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
    db: AsyncSession = Depends(get_db)
):
    # Check if the prescription exists in the database
    prescription = await db.execute(select(Prescription).filter(Prescription.prescription_id == prescription_id))
    prescription = prescription.scalars().first()
    if not prescription:
        raise HTTPException(
            status_code=404,
            detail=f"Prescription with id {prescription_id} not found."
        )

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
async def delete_prescription_detail(prescription_id: int, medication_id: int, db: AsyncSession = Depends(get_db)):
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














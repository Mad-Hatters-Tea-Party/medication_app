#This is the pydantic file for validating data in different senerios
# like updating table, creating tables, reading tables, etc
# More validation checks can be added as we move forward in the project
# have to install the pydantic email thing 
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta  # For calculating age

# ===================== User =====================
# Helper function to calculate age from date of birth
def calculate_age(dob: datetime) -> int:
    # Make sure dob is timezone-aware, if it is not already
    if dob.tzinfo is None:
        dob = dob.replace(tzinfo=timezone.utc)  # Assuming UTC if dob is naive

    today = datetime.now(timezone.utc)  # Current UTC time
    delta = relativedelta(today, dob)  # Get the difference between today and the DOB
    return delta.years  # Return the age in years

class UserCreate(BaseModel):
    user_id: str = Field(..., max_length=25)
    user_email: Optional[EmailStr] = None
    user_phone: Optional[str] = Field(None, max_length=20)
    user_pwd: str = Field(..., min_length=8, max_length=45)  # Password length check
    user_gender: Optional[int] = Field(None, ge=0, le=1)  # Gender is 0(female) or 1(male)
    user_dob: Optional[datetime] = None
    user_height: Optional[int] = Field(None, gt=0)  # Height must be greater than 0
    user_weight: Optional[int] = Field(None, gt=0)  # Weight must be greater than 0

    @field_validator("user_dob", mode="before")
    def check_age(cls, v):
        if v:
            age = calculate_age(v)
            if age < 18:
                raise ValueError('Age must be 18 or older')
            if age > 120:
                raise ValueError('Age must be 120 or younger')
        return v

class UserUpdate(BaseModel):
    user_email: Optional[EmailStr] = None
    user_phone: Optional[str] = Field(None, max_length=20)
    user_pwd: Optional[str] = Field(None, min_length=8, max_length=45)  # Password length check
    user_gender: Optional[int] = Field(None, ge=0, le=1)  # Gender is 0(female) or 1(male)
    user_dob: Optional[datetime] = None
    user_height: Optional[int] = Field(None, gt=0)  # Height must be greater than 0
    user_weight: Optional[int] = Field(None, gt=0)  # Weight must be greater than 0

    @field_validator("user_dob", mode="before")
    def check_age(cls, v):
        if v:
            age = calculate_age(v)
            if age < 18:
                raise ValueError('Age must be 18 or older')
            if age > 120:
                raise ValueError('Age must be 120 or younger')
        return v

class UserRead(BaseModel):
    user_id: str
    user_email: Optional[EmailStr] = None
    user_phone: Optional[str] = None
    user_gender: Optional[int] = None
    user_dob: Optional[datetime] = None
    user_height: Optional[int] = None
    user_weight: Optional[int] = None
    class Config:
        from_orm = True

class UserDelete(BaseModel):
    user_id: str
    user_pwd: str


# ===================== Medication =====================


class MedicationRead(BaseModel):
    medication_id: int
    medication_name: Optional[str] = Field(None, max_length=45)  # Max length 45 for medication name
    medication_use: Optional[str] = Field(None, max_length=255)  # Assuming max 255 characters for use description

    class Config:
        from_orm = True



# ===================== Notification =====================

class NotificationCreate(BaseModel):
    user_id: str
    notification_type: Optional[int] = Field(None, ge=1, le=2, description="Notification type: 1 for refill, 2 for reminder")
    notification_message: Optional[str] = Field(None, max_length=150)  # Max length 150 for message
    notification_date: Optional[datetime] = None
    notification_status: Optional[int] = Field(None, ge=0, le=1, description="Notification status: 0 for sent, 1 for read")

class NotificationUpdate(BaseModel):
    notification_type: Optional[int] = Field(None, ge=1, le=2, description="Notification type: 1 for refill, 2 for reminder")
    notification_message: Optional[str] = Field(None, max_length=150)  # Max length 150 for message
    notification_date: Optional[datetime] = None
    notification_status: Optional[int] = Field(None, ge=0, le=1, description="Notification status: 0 for sent, 1 for read")

class NotificationRead(BaseModel):
    notification_id: int
    user_id: str
    notification_type: Optional[int] = None 
    notification_message: Optional[str] = None
    notification_date: Optional[datetime] = None
    notification_status: Optional[int] = None

    class Config:
        from_orm = True

class NotificationDelete(BaseModel):
    notification_id: int


# ===================== Prescription =====================

class PrescriptionCreate(BaseModel):
    user_id: str
    prescription_date_start: Optional[datetime] = None
    prescription_date_end: Optional[datetime] = None
    prescription_status: Optional[int] = Field(None, ge=0, le=1, description="0 = active, 1 = archive")

class PrescriptionUpdate(BaseModel):
    prescription_date_start: Optional[datetime] = None
    prescription_date_end: Optional[datetime] = None
    prescription_status: Optional[int] = Field(None, ge=0, le=1, description="0 = active, 1 = archive")

class PrescriptionRead(BaseModel):
    prescription_id: int
    user_id: str
    prescription_date_start: Optional[datetime] = None
    prescription_date_end: Optional[datetime] = None
    prescription_status: Optional[int] = None
    prescription_details: List["PrescriptionDetailRead"] = []

    class Config:
        from_orm = True

class PrescriptionDelete(BaseModel):
    prescription_id: int


# ===================== PrescriptionDetail =====================

class PrescriptionDetailCreate(BaseModel):
    medication_id: int
    presc_dose: Optional[str] = Field(None, max_length=10)  # Max length 10 for dose
    presc_qty: Optional[int] = None
    presc_type: Optional[str] = Field(None, max_length=15)  # Max length 15 for type (e.g., Grams, Milligrams, Drops)
    presc_frequency: Optional[str] = Field(None, max_length=45)  # Max length 45 for frequency

class PrescriptionDetailUpdate(BaseModel):
    presc_dose: Optional[str] = Field(None, max_length=10)  # Max length 10 for dose
    presc_qty: Optional[int] = None
    presc_type: Optional[str] = Field(None, max_length=15)  # Max length 15 for type (e.g., Grams, Milligrams, Drops)
    presc_frequency: Optional[str] = Field(None, max_length=45)  # Max length 45 for frequency

class PrescriptionDetailRead(BaseModel):
    prescription_id: int
    medication_id: int
    presc_dose: Optional[str] = Field(None, max_length=10)  # Max length 10 for dose
    presc_qty: Optional[int] = None
    presc_type: Optional[str] = Field(None, max_length=15)  # Max length 15 for type
    presc_frequency: Optional[str] = Field(None, max_length=45)  # Max length 45 for frequency

    class Config:
        from_orm = True

class PrescriptionDetailDelete(BaseModel):
    prescription_id: int
    medication_id: int


# ===================== SideEffect =====================

class SideEffectCreate(BaseModel):
    user_id: str
    medication_id: int
    side_effect_desc: Optional[str] = Field(None, max_length=255)  # Max length 255 for description
    side_effect_date: Optional[datetime] = None

class SideEffectUpdate(BaseModel):
    side_effect_desc: Optional[str] = Field(None, max_length=255)  # Max length 255 for description
    side_effect_date: Optional[datetime] = None

class SideEffectRead(BaseModel):
    side_effects_id: int
    user_id: str
    medication_id: int
    side_effect_desc: Optional[str] = Field(None, max_length=255)  # Max length 255 for description
    side_effect_date: Optional[datetime] = None

    class Config:
        from_orm = True

class SideEffectDelete(BaseModel):
    side_effects_id: int





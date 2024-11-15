#This is the pydantic file for validating data in different senerios
# like updating table, creating tables, reading tables, etc
# More validation checks can be added as we move forward in the project
# have to install the pydantic email thing 
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

# ===================== User =====================

class UserCreate(BaseModel):
    user_id: str
    user_email: Optional[EmailStr] = None
    user_phone: Optional[str] = None
    user_pwd: str
    user_gender: Optional[int] = Field(None, ge=0, le=1)  # Gender is 0(female) or 1(male)
    user_dob: Optional[datetime] = None
    user_height: Optional[int] = Field(None, gt=0)  # Height must be greater than 0
    user_weight: Optional[int] = Field(None, gt=0)  # Weight must be greater than 0

class UserUpdate(BaseModel):
    user_email: Optional[EmailStr] = None
    user_phone: Optional[str] = None
    user_pwd: Optional[str] = None
    user_gender: Optional[int] = Field(None, ge=0, le=1)  # Gender is 0(female) or 1(male)
    user_dob: Optional[datetime] = None
    user_height: Optional[int] = Field(None, gt=0)  # Height must be greater than 0
    user_weight: Optional[int] = Field(None, gt=0)  # Weight must be greater than 0

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
    medication_name: Optional[str] = None
    medication_use: Optional[str] = None

    class Config:
        from_orm = True



# ===================== Notification =====================

class NotificationCreate(BaseModel):
    user_id: str
    notification_type: Optional[int] = Field(None, ge=1, le=2, description="Notification type: 1 for refill, 2 for reminder")
    notification_message: Optional[str] = None
    notification_date: Optional[datetime] = None
    nnotification_status: Optional[int] = Field(None, ge=0, le=1, description="Notification status: 0 for sent, 1 for read")

class NotificationUpdate(BaseModel):
    notification_type: Optional[int] = Field(None, ge=1, le=2, description="Notification type: 1 for refill, 2 for reminder")
    notification_message: Optional[str] = None
    notification_date: Optional[datetime] = None
    nnotification_status: Optional[int] = Field(None, ge=0, le=1, description="Notification status: 0 for sent, 1 for read")

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
    prescription_status: Optional[int] = None

class PrescriptionUpdate(BaseModel):
    prescription_date_start: Optional[datetime] = None
    prescription_date_end: Optional[datetime] = None
    prescription_status: Optional[int] = None

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
    presc_dose: Optional[str] = None
    presc_qty: Optional[int] = None
    presc_type: Optional[str] = None
    presc_frequency: Optional[str] = None

class PrescriptionDetailUpdate(BaseModel):
    presc_dose: Optional[str] = None
    presc_qty: Optional[int] = None
    presc_type: Optional[str] = None
    presc_frequency: Optional[str] = None

class PrescriptionDetailRead(BaseModel):
    prescription_id: int
    medication_id: int
    presc_dose: Optional[str] = None
    presc_qty: Optional[int] = None
    presc_type: Optional[str] = None
    presc_frequency: Optional[str] = None

    class Config:
        from_orm = True

class PrescriptionDetailDelete(BaseModel):
    prescription_id: int
    medication_id: int


# ===================== SideEffect =====================

class SideEffectCreate(BaseModel):
    user_id: str
    medication_id: int
    side_effect_desc: Optional[str] = None
    side_effect_date: Optional[datetime] = None

class SideEffectUpdate(BaseModel):
    side_effect_desc: Optional[str] = None
    side_effect_date: Optional[datetime] = None

class SideEffectRead(BaseModel):
    side_effect_id: int
    user_id: str
    medication_id: int
    side_effect_desc: Optional[str] = None
    side_effect_date: Optional[datetime] = None

    class Config:
        from_orm = True

class SideEffectDelete(BaseModel):
    side_effect_id: int


#This is the pydantic file for validating data in different senerios
# like updating table, creating tables, reading tables, etc
# More validation checks can be added as we move forward in the project
# have to install the pydantic email thing 
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator
from typing import Optional, List
from datetime import datetime, timezone, date
from dateutil.relativedelta import relativedelta  # For calculating age
from pydantic import ValidationError # for testing validation cases 

# ===================== User =====================
# Base class to avoid repeating Config in every model
class BaseORMModel(BaseModel):
    class Config:
        from_orm = True
        from_attributes = True
# ================= Token ================================
# Token model returned to the client after authentication
class Token(BaseORMModel):
    access_token: str
    token_type: str

# TokenData model to decode JWT payload and retrieve user data
class TokenData(BaseORMModel):
    username: Optional[str] = None
# Function to convert a string to a date object
def str_to_date(date_str: str, format: str = "%Y-%m-%d") -> date:
    """
    Convert a string to a date object.
    
    :param date_str: The string representing the date.
    :param format: The format of the date string. Default is "%Y-%m-%d".
    :return: A date object.
    """
    try:
        return datetime.strptime(date_str, format).date()
    except ValueError:
        raise ValueError(f"Invalid date string format. Expected format: {format}.")
  # Function to convert a date object to a str
def date_to_str(date_obj: date, format: str = "%Y-%m-%d") -> str:
    """
    Convert a date object to a string.
    
    :param date_obj: The date object to convert.
    :param format: The format of the resulting date string. Default is "%Y-%m-%d".
    :return: A string representing the formatted date.
    """
    try:
        return date_obj.strftime(format)
    except AttributeError:
        raise ValueError("The provided object is not a valid date object.")
    except Exception as e:
        raise ValueError(f"An error occurred while formatting the date: {e}")
        

# Helper function to convert datetime to string
def datetime_to_str(dt: datetime, format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Convert a datetime object to a string representation in the specified format.
    Default format is "%Y-%m-%d %H:%M:%S".

    :param dt: datetime object to convert.
    :param format: The format for the output string. Default is "%Y-%m-%d %H:%M:%S".
    :return: A string representation of the datetime object.
    """
    if not isinstance(dt, datetime):
        raise TypeError("Expected a datetime object.")
    return dt.strftime(format)
# Helper function to convert string to datetime object
def str_to_datetime(date_str: str, format: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """
    Convert a string representation of date/time to a datetime object.
    Default format is "%Y-%m-%d %H:%M:%S".

    :param date_str: The string to convert.
    :param format: The format of the input string. Default is "%Y-%m-%d %H:%M:%S".
    :return: A datetime object.
    """
    try:
        return datetime.strptime(date_str, format)
    except ValueError:
        raise ValueError(f"Invalid date string format. Expected format: {format}.")

# Helper function to calculate age from date of birth (using date object instead of date time object)
def calculate_age(dob: date) -> int:
    if not isinstance(dob, date):
        raise TypeError("Expected a date object for dob")
    
    today = date.today()  # Get today's date
    delta = relativedelta(today, dob)  # Get the difference between today and the DOB
    return delta.years  # Return the age in years
# Reusable Validator for Weight
def validate_weight(value: Optional[int]) -> Optional[int]:
    if value is not None:
        if not (0 < value < 700):
            raise ValueError("Weight must be greater than 0 and less than 700.")
    return value

# Reusable Validator for Height
def validate_height(value: Optional[int]) -> Optional[int]:
    if value is not None:
        if not (0 < value < 96):
            raise ValueError("Height must be greater than 0 and less than 96.")
    return value
# Helper function to convert height from inches to meters
def inches_to_meters(inches: Optional[int]) -> Optional[float]:
    if inches is not None:
        return inches * 0.0254  # Convert inches to meters
    return None

# Helper function to convert weight from pounds to kilograms
def pounds_to_kg(pounds: Optional[int]) -> Optional[float]:
    if pounds is not None:
        return pounds * 0.453592  # Convert pounds to kilograms
    return None

# Helper function to calculate BMI
def calculate_bmi(height_in: Optional[int], weight_lb: Optional[int]) -> Optional[float]:
    # Convert height and weight to metric units
    height_m = inches_to_meters(height_in)  # height in meters
    weight_kg = pounds_to_kg(weight_lb)  # weight in kg
    
    if height_m and weight_kg:
        # BMI formula: weight (kg) / height (m)^2
        bmi = weight_kg / (height_m ** 2)
        return round(bmi, 2)
    return None

class UserLogin(BaseORMModel):
    user_id: str = Field(..., max_length=25)
    user_pwd: str = Field(..., min_length=8, max_length=45)  # Password length check

class UserCreate(BaseORMModel):
    user_id: str = Field(..., max_length=25)
    user_email: Optional[EmailStr] = None
    user_phone: Optional[str] = Field(None, max_length=20)
    user_pwd: str = Field(..., min_length=8, max_length=45)  # Password length check
    user_gender: Optional[int] = Field(None, ge=0, le=1)  # Gender is 0(female) or 1(male)
    user_dob: date
    user_height: int = Field(gt=0, lt=96)  # Height must be >0 and <96
    user_weight: int = Field(gt=0, lt=700)  # Weight must be >0 and <700
    #user_bmi: Optional[float] = None  # BMI field to be calculated
        
    @model_validator(mode="before")
    def validate(cls, values):
        # Convert user_dob if it is a string
        dob = values.get('user_dob')
        if isinstance(dob, str):
            dob = str_to_date(dob)  # Use the helper function to convert str to date
            values['user_dob'] = dob
        
        # Validate user_dob for age
        if dob is None:
            raise ValueError("user_dob is required.")
        
        age = calculate_age(dob)
        if age < 18:
            raise ValueError('Age must be 18 or older')
        if age > 120:
            raise ValueError('Age must be 120 or younger')
        
        
        # Validate user_weight
        weight = values.get('user_weight')
        if weight is None or weight <= 0 or weight >= 700:
            raise ValueError("Weight must be between 1 and 700 pounds.")
        
        # Validate user_height
        height = values.get('user_height')
        if height is None or height <= 0 or height >= 96:
            raise ValueError("Height must be between 1 and 95 inches.")

        return values
    

class UserUpdate(BaseORMModel):
    user_email: Optional[EmailStr] = None
    user_phone: Optional[str] = Field(None, max_length=20)
    user_gender: Optional[int] = Field(None, ge=0, le=1)  # Gender is 0(female) or 1(male)
    user_dob: Optional[date] = None
    user_height: Optional[int] = Field(None, gt=0, lt=96)  # Height must be >0 and <96
    user_weight: Optional[int] = Field(None, gt=0, lt=700)  # Weight must be >0 and <700
    user_pwd: Optional[str] = None  # Old password (for verification)
    user_old_pwd: Optional[str] = None  # Old password (for verification)
   # user_bmi: Optional[float] = None  # BMI field to be calculated
    
    @model_validator(mode="before")
    def validate(cls, values):
        # Convert user_dob if it is a string
        dob = values.get('user_dob')
        if dob is None:
            pass
        elif isinstance(dob, str):
            dob = str_to_date(dob)  # Use the helper function to convert str to date
            values['user_dob'] = dob
            age = calculate_age(dob)
            if age < 18:
                raise ValueError('Age must be 18 or older')
            if age > 120:
                raise ValueError('Age must be 120 or younger')
        # Validate user_dob for age
        #if dob is None:
            #raise ValueError("user_dob is required.")
        
        #age = calculate_age(dob)
       # if age < 18:
           # raise ValueError('Age must be 18 or older')
       # if age > 120:
            #raise ValueError('Age must be 120 or younger')
        
        
        # Validate user_weight
        weight = values.get('user_weight')
        if weight is None:
            pass 
        elif weight <= 0 or weight >= 700:
            raise ValueError("Weight must be between 1 and 700 pounds.")
        
        # Validate user_height
        height = values.get('user_height')
        if height is None:
            pass 
        elif height <= 0 or height >= 96:
            raise ValueError("Height must be between 1 and 95 inches.")
        
        
        return values
    
class PasswordUpdateResponse(BaseORMModel):
    msg: str
    user_id: str
    
class UserRead(BaseORMModel):
    user_id: str
    user_email: Optional[EmailStr] = None
    user_phone: Optional[str] = None
    user_gender: Optional[int] = None
    user_dob: Optional[date] = None
    user_height: Optional[int] # Height in inches
    user_weight: Optional[int] # Weight in pounds
    user_bmi: Optional[float] # BMI value
    created_at: datetime
    updated_at: datetime

    @field_validator('created_at', mode='before')
    def convert_created_at_to_str(cls, v):
        if isinstance(v, datetime):
            return datetime_to_str(v)
        if v is None:
            return v  # or handle default date formatting
        raise TypeError(f"Expected datetime, got {type(v)}")

    @field_validator('updated_at', mode='before')
    def convert_updated_at_to_str(cls, v):
        # Convert datetime to string
        if isinstance(v, datetime):
            return datetime_to_str(v)
        return v
    @field_validator('user_dob', mode='before')
    def parse_user_dob(cls, v):
        # Convert string to datetime if necessary
        if isinstance(v, str):
            return str_to_datetime(v, "%Y-%m-%d")
        return v
    
    @model_validator(mode="before")
    def validate_and_calculate_bmi(cls, values):
        # Validate user_weight (1 to 700 pounds)
        weight = getattr(values, 'user_weight', None)  # Default to None if user_weight is not provided
        height = getattr(values, 'user_height', None)  # Default to None if user_height is not provided

          # If both weight and height are None, skip validation and calculation
          # If both weight and height are None, skip validation and calculation
        if weight is None and height is None:
            return values

        if weight is not None and (weight <= 0 or weight >= 700):
            raise ValueError("Weight must be between 1 and 700 pounds.")
        
        # Validate user_height (1 to 95 inches)
        if height is not None and (height <= 0 or height >= 96):
            raise ValueError("Height must be between 1 and 95 inches.")
        
        # If BMI is not provided, calculate it if both weight and height are provided
        if height is not None and weight is not None:
            bmi = calculate_bmi(height, weight)
            values.user_bmi = bmi  # Set the calculated BMI
        else: 
            bmi = None

        return values
    
    
class UserDelete(BaseORMModel):
    user_id: str
    user_pwd: str

# Pydantic model for the delete response
class UserDeleteResponse(BaseORMModel):
    msg: str
    user_id: str

class UserResponse(BaseORMModel):
    user: UserRead
    token_info: Token
    
# Test cases for different dates of birth
'''test_dates = [
    date(2005, 10, 10),  # Age should be below 18 (invalid)
    date(2000, 10, 10),  # Age should be 24 (valid)
    date(1900, 10, 10),  # Age should be above 120 (invalid)
    date(1990, 10, 10),  # Age should be 34 (valid)
    date(2003, 10, 10),  # Age should be 21 (valid)
]

# Iterate over test cases
for dob in test_dates:
    try:
        # Try to create a UserCreate instance with each date of birth
        user = UserCreate(user_id="test_user", user_dob=dob, user_pwd="strongpassword123")
        print(f"User created successfully with DOB: {dob} (Age: {calculate_age(dob)})")
    except ValidationError as e:
        print(f"Validation Error for DOB {dob}: {e}")'''


# ===================== Medication =====================


class MedicationRead(BaseORMModel):
    medication_id: int
    medication_name: Optional[str] = Field(None, max_length=45)  # Max length 45 for medication name
    medication_use: Optional[str] = Field(None, max_length=255)  # Assuming max 255 characters for use description



# ===================== Notification =====================

class NotificationCreate(BaseORMModel):
   # user_id: str
    notification_type: Optional[int] = Field(None, ge=1, le=2, description="Notification type: 1 for refill, 2 for reminder")
    notification_message: Optional[str] = Field(None, max_length=150)  # Max length 150 for message
    notification_date: Optional[datetime] = None
    #notification_status: Optional[int] = Field(None, ge=0, le=1, description="Notification status: 0 for sent, 1 for read")

class NotificationUpdate(BaseORMModel):
    notification_type: Optional[int] = Field(None, ge=1, le=2, description="Notification type: 1 for refill, 2 for reminder")
    notification_message: Optional[str] = Field(None, max_length=150)  # Max length 150 for message
    notification_date: Optional[datetime] = None
    notification_status: Optional[int] = Field(None, ge=0, le=1, description="Notification status: 0 for sent, 1 for read")

class NotificationRead(BaseORMModel):
    notification_id: int
    user_id: str
    notification_type: Optional[int] = None 
    notification_message: Optional[str] = None
    notification_date: Optional[datetime] = None
    notification_status: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    @field_validator('created_at', mode='before')
    def convert_created_at_to_str(cls, v):
        if isinstance(v, datetime):
            return datetime_to_str(v)
        if v is None:
            return v  # or handle default date formatting
        raise TypeError(f"Expected datetime, got {type(v)}")

    @field_validator('updated_at', mode='before')
    def convert_updated_at_to_str(cls, v):
        # Convert datetime to string
        if isinstance(v, datetime):
            return datetime_to_str(v)
        return v

class NotificationDelete(BaseORMModel):
    notification_id: int

class NotificationDeleteResponse(BaseORMModel):
    msg: str
    notification_id: int

# ===================== Prescription =====================

class PrescriptionCreate(BaseORMModel):
    #user_id: str
    prescription_date_start: Optional[date] = None
    prescription_date_end: Optional[date] = None
    prescription_status: Optional[int] = Field(None, ge=0, le=1, description="0 = active, 1 = archive")

    # Validate and convert the date string to datetime using field_validator
    @field_validator('prescription_date_start', mode='before')
    def validate_prescription_date_start(cls, v):
        if v:
            return str_to_date(v)
        return v

    @field_validator('prescription_date_end', mode='before')
    def validate_prescription_date_end(cls, v):
        if v:
            return str_to_date(v)
        return v


class PrescriptionUpdate(BaseORMModel):
    prescription_date_start: Optional[date] = None
    prescription_date_end: Optional[date] = None
    prescription_status: Optional[int] = Field(None, ge=0, le=1, description="0 = active, 1 = archive")

    # Validate and convert the date string to datetime using field_validator
    @field_validator('prescription_date_start', mode='before')
    def validate_prescription_date_start(cls, v):
        if v:
            return str_to_date(v)
        return v

    @field_validator('prescription_date_end', mode='before')
    def validate_prescription_date_end(cls, v):
        if v:
            return str_to_date(v)
        return v

class PrescriptionRead(BaseORMModel):
    prescription_id: int
    user_id: str
    prescription_date_start: Optional[date] = None
    prescription_date_end: Optional[date] = None
    prescription_status: Optional[int] = None
    prescription_details: List["PrescriptionDetailRead"] = []  # Default to an empty list

    @field_validator('prescription_date_start', mode='before')
    def convert_created_at_to_str(cls, v):
        if isinstance(v, date):
            return date_to_str(v)
        if v is None:
            return v  # or handle default date formatting
        raise TypeError(f"Expected datetime, got {type(v)}")

    @field_validator('prescription_date_end', mode='before')
    def convert_updated_at_to_str(cls, v):
        # Convert datetime to string
        if isinstance(v, date):
            return date_to_str(v)
        return v

class PrescriptionDelete(BaseORMModel):
    prescription_id: int

class PrescriptionDeleteResponse(BaseORMModel):
    msg: str
    prescription_id: int


# ===================== PrescriptionDetail =====================

class PrescriptionDetailCreate(BaseORMModel):
    medication_id: int
    presc_dose: Optional[str] = Field(None, max_length=10)  # Max length 10 for dose
    presc_qty: Optional[int] = None
    presc_type: Optional[str] = Field(None, max_length=15)  # Max length 15 for type (e.g., Grams, Milligrams, Drops)
    presc_frequency: Optional[str] = Field(None, max_length=45)  # Max length 45 for frequency

class PrescriptionDetailUpdate(BaseORMModel):
    presc_dose: Optional[str] = Field(None, max_length=10)  # Max length 10 for dose
    presc_qty: Optional[int] = None
    presc_type: Optional[str] = Field(None, max_length=15)  # Max length 15 for type (e.g., Grams, Milligrams, Drops)
    presc_frequency: Optional[str] = Field(None, max_length=45)  # Max length 45 for frequency

class PrescriptionDetailRead(BaseORMModel):
    prescription_id: int
    medication_id: int
    medication_name: Optional[str] = None  # Added field for medication name
    presc_dose: Optional[str] = Field(None, max_length=10)  # Max length 10 for dose
    presc_qty: Optional[int] = None
    presc_type: Optional[str] = Field(None, max_length=15)  # Max length 15 for type
    presc_frequency: Optional[str] = Field(None, max_length=45)  # Max length 45 for frequency
    



class PrescriptionDetailDelete(BaseORMModel):
    prescription_id: int
    medication_id: int
class PrescriptionDetailDeleteResponse(BaseORMModel):
    msg: str
    prescription_id: int
    medication_id: int

# ===================== SideEffect =====================

class SideEffectCreate(BaseORMModel):
    #user_id: str
    medication_id: int
    side_effect_desc: Optional[str] = Field(None, max_length=255)  # Max length 255 for description


class SideEffectUpdate(BaseORMModel):
    side_effect_desc: Optional[str] = Field(None, max_length=255)  # Max length 255 for description


class SideEffectRead(BaseORMModel):
    side_effects_id: int
    user_id: str
    medication_id: int
    side_effect_desc: Optional[str] = Field(None, max_length=255)  # Max length 255 for description
    created_at: datetime
    updated_at: datetime
    @field_validator('created_at', mode='before')
    def convert_created_at_to_str(cls, v):
        if isinstance(v, datetime):
            return datetime_to_str(v)
        if v is None:
            return v  # or handle default date formatting
        raise TypeError(f"Expected datetime, got {type(v)}")

    @field_validator('updated_at', mode='before')
    def convert_updated_at_to_str(cls, v):
        # Convert datetime to string
        if isinstance(v, datetime):
            return datetime_to_str(v)
        return v

class SideEffectDelete(BaseORMModel):
    side_effects_id: int

class SideEffectDeleteResponse(BaseORMModel):
    msg:str
    side_effects_id: int





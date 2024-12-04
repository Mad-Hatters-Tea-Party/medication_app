
# This is the file for creating the SQL aclchemy schema and tables -- reflects the tables and relationships in the database

from sqlalchemy import (
    create_engine, Integer, String, DateTime, ForeignKey, Text, Date
)
from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column
from typing import Optional, List
from sqlalchemy.sql import func
from datetime import datetime

# Base class for models
Base = declarative_base()
#class Base(declarative_base()):
    #pass

class User(Base):
    __tablename__ = 'user'
    
    user_id: Mapped[str] = mapped_column(String(25), primary_key=True)
    user_email: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment='This is the email address of the user.')
    user_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment='User phone number: Country code + number. Eg. 44 720192837')
    user_pwd: Mapped[str] = mapped_column(String(255), nullable=False)  # Password cannot be null
    user_gender: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment='0 = female, 1 = male')
    user_dob: Mapped[Date] = mapped_column(Date, nullable=False, comment='User date of birth.')
    user_height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment='Height in inches.')
    user_weight: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment='Weight in pounds.')
    # user_bmi: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment='BMI formula = weight(kg) / height(m)^2')

    # Timestamps to track when the user is created or updated
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), comment="Creation timestamp")
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), comment="Last update timestamp")
    

    # Relationships
    notifications: Mapped[List['Notification']] = relationship('Notification', back_populates='user', cascade='all, delete-orphan')
    prescriptions: Mapped[List['Prescription']] = relationship('Prescription', back_populates='user', cascade='all, delete-orphan')
    side_effects: Mapped[List['SideEffect']] = relationship('SideEffect', back_populates='user', cascade='all, delete-orphan')


class Medication(Base):
    __tablename__ = 'medication'
    
    medication_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    medication_name: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    medication_use: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    side_effects: Mapped[List['SideEffect']] = relationship('SideEffect', back_populates='medication')
    prescription_details: Mapped[List['PrescriptionDetail']] = relationship('PrescriptionDetail', back_populates='medication')
# Define the __repr__ method to return a more human-readable string for the object
    def __repr__(self):
        return f"<Medication(id={self.medication_id}, name={self.medication_name}, use={self.medication_use})>"


class Notification(Base):
    __tablename__ = 'notification'
    
    notification_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(25), ForeignKey('user.user_id'))
    notification_type: Mapped[int] = mapped_column(Integer, nullable=False, comment='1 = refill, 2 = reminder')
    notification_message: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    notification_date: Mapped[Optional[DateTime]] = mapped_column(DateTime, nullable=True)
    notification_status: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment='0 = sent, 1 = read')

     # Timestamps to track when the user is created or updated
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), comment="Creation timestamp")
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), comment="Last update timestamp")

    #relationships 
    user: Mapped[User] = relationship('User', back_populates='notifications')


class Prescription(Base):
    __tablename__ = 'prescription'
    
    prescription_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    prescription_date_start: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)
    prescription_date_end: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)
    prescription_status: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment='0 = active, 1 = archive')
    user_id: Mapped[str] = mapped_column(String(25), ForeignKey('user.user_id'))

    user: Mapped[User] = relationship('User', back_populates='prescriptions')
    prescription_details: Mapped[List['PrescriptionDetail']] = relationship('PrescriptionDetail', back_populates='prescription', cascade='all, delete-orphan', lazy="selectin")


class PrescriptionDetail(Base):
    __tablename__ = 'prescription_detail'
    
    prescription_id: Mapped[int] = mapped_column(Integer, ForeignKey('prescription.prescription_id'), primary_key=True)
    medication_id: Mapped[int] = mapped_column(Integer, ForeignKey('medication.medication_id'), primary_key=True)
    presc_dose: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    presc_qty: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    presc_type: Mapped[Optional[str]] = mapped_column(String(15), nullable=True, comment='Grams, Milligrams, Drops')
    presc_frequency: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)

    medication: Mapped[Medication] = relationship('Medication', back_populates='prescription_details')
    prescription: Mapped[Prescription] = relationship('Prescription', back_populates='prescription_details')


class SideEffect(Base):
    __tablename__ = 'side_effect'
    
    side_effects_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(25), ForeignKey('user.user_id'))
    medication_id: Mapped[int] = mapped_column(Integer, ForeignKey('medication.medication_id'))
    side_effect_desc: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    #remove date from database use timstamps below instead 
    #side_effect_date: Mapped[Optional[DateTime]] = mapped_column(DateTime, nullable=True)

    user: Mapped[User] = relationship('User', back_populates='side_effects')
    medication: Mapped[Medication] = relationship('Medication', back_populates='side_effects')

    # Timestamps to track when the user is created or updated
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), comment="Creation timestamp")
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), comment="Last update timestamp")



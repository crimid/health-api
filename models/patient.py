from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Patient(SQLModel, table=True):
    """Patient model linked to User"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    doctor_id: Optional[int] = Field(foreign_key="user.id")
    medical_history: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PatientCreate(SQLModel):
    """Model for creating a patient record"""
    user_id: int
    doctor_id: Optional[int] = None
    medical_history: Optional[str] = None

class PatientUpdate(SQLModel):
    """Model for updating a patient record"""
    doctor_id: Optional[int] = None
    medical_history: Optional[str] = None

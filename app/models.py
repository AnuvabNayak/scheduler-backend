import uuid
from typing import Optional, List
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlmodel import Field, SQLModel, Column, DateTime, Relationship
from enum import Enum

# Define IST globally for consistency
IST = ZoneInfo("Asia/Kolkata")

def get_current_time():
    """Returns Timezone-Aware current time in IST"""
    return datetime.now(IST)

# ENUMS
class AppointmentStatus(str, Enum):
    INITIATED = "initiated"         # Created, waiting for user input
    WINDOW_SELECTED = "window_selected" # User picked a slot
    CONFIRMED = "confirmed"         # Employee locked the time
    REJECTED = "rejected"           # Employee rejects it
    COMPLETED = "completed"         # Call happen

class TimeWindow(str, Enum):
    MORNING = "morning"     # 9am - 12pm
    AFTERNOON = "afternoon" # 12pm - 4pm
    EVENING = "evening"     # 4pm - 7pm

# DATABASE MODELS:

class Lead(SQLModel, table=True):
    __tablename__ = "leads"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    whatsapp_number: str = Field(index=True, unique=True)
    name: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(
        default_factory=get_current_time,
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )

    # One Lead has many Appointments
    appointments: List["Appointment"] = Relationship(back_populates="lead")

class Appointment(SQLModel, table=True):
    __tablename__ = "appointments"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    # Foreign Key
    lead_id: uuid.UUID = Field(foreign_key="leads.id")
    
    # Logic State
    status: AppointmentStatus = Field(default=AppointmentStatus.INITIATED)
    
    # Client Inputs
    preferred_date: Optional[datetime] = Field(
        default=None, 
        sa_column=Column(DateTime(timezone=True))
    )
    preferred_window: Optional[TimeWindow] = None
    
    # Employee Inputs
    confirmed_time: Optional[datetime] = Field(
        default=None, 
        sa_column=Column(DateTime(timezone=True))
    )
    employee_notes: Optional[str] = None
    
    # Metadata
    updated_at: datetime = Field(
        default_factory=get_current_time,
        sa_column=Column(DateTime(timezone=True), onupdate=get_current_time)
    )

    # Relationship: An Appointment belongs to one Lead
    lead: Lead = Relationship(back_populates="appointments")
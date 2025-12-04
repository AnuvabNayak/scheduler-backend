from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from .models import Lead, Appointment, AppointmentStatus, TimeWindow

# LEAD OPERATIONS

async def get_appointment_by_lead(session: AsyncSession, lead_id: str):
    """
    Fetches the most recent appointment for a specific lead.
    Used by the Frontend Booking page to validate the user.
    """
    statement = select(Appointment).where(Appointment.lead_id == lead_id).order_by(Appointment.created_at.desc())
    result = await session.exec(statement)
    return result.first()

async def get_lead_by_phone(session: AsyncSession, phone: str):
    statement = select(Lead).where(Lead.whatsapp_number == phone)
    result = await session.exec(statement)
    return result.first()

async def create_lead(session: AsyncSession, phone: str, name: str = None):
    lead = Lead(whatsapp_number=phone, name=name)
    session.add(lead)
    await session.commit()
    await session.refresh(lead)
    return lead

# APPOINTMENT OPERATIONS

async def get_open_appointment(session: AsyncSession, lead_id):
    """
    Checks if the lead has an active appointment that isn't completed or rejected.
    Fixes the 'Double Booking' Risk.
    """
    statement = select(Appointment).where(
        Appointment.lead_id == lead_id,
        Appointment.status.in_([
            AppointmentStatus.INITIATED, 
            AppointmentStatus.WINDOW_SELECTED, 
            AppointmentStatus.CONFIRMED
        ])
    )
    result = await session.exec(statement)
    return result.first()

async def create_initial_appointment(session: AsyncSession, lead_id):
    appointment = Appointment(lead_id=lead_id, status=AppointmentStatus.INITIATED)
    session.add(appointment)
    await session.commit()
    await session.refresh(appointment)
    return appointment

async def update_appointment_window(session: AsyncSession, appointment_id, date: datetime, window: TimeWindow):
    """
    Updates the window ONLY if the appointment is in a valid state.
    Fixes the 'State Overwrite' Risk.
    """
    appointment = await session.get(Appointment, appointment_id)
    
    if not appointment:
        raise ValueError("Appointment not found")
        
    # Don't allow changing confirmed appointments
    
    if appointment.status == AppointmentStatus.CONFIRMED:
        raise ValueError("Cannot reschedule a confirmed appointment without agent approval.")

    appointment.preferred_date = date
    appointment.preferred_window = window
    appointment.status = AppointmentStatus.WINDOW_SELECTED
    
    session.add(appointment)
    await session.commit()
    await session.refresh(appointment)
    return appointment
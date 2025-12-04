from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession # <--- Changed from sqlmodel.Session
from ..database import get_session
from .. import crud, schemas, models # Ensure schemas is imported
from datetime import datetime
from zoneinfo import ZoneInfo

router = APIRouter(prefix="/scheduling", tags=["Scheduling"])

@router.get("/lead/{lead_id}")
async def get_lead_status(lead_id: str, session: AsyncSession = Depends(get_session)):
    # Use in Frontend to check who the user is
    appointment = await crud.get_appointment_by_lead(session, lead_id) # <--- Awaited
    if not appointment:
        raise HTTPException(status_code=404, detail="No appointment found")
    return appointment

@router.post("/select-window")
async def select_window(
    request: schemas.WindowSelectionRequest, 
    session: AsyncSession = Depends(get_session)
):
    try:
        dt_naive = datetime.strptime(request.date_str, "%Y-%m-%d")
        dt_ist = dt_naive.replace(tzinfo=ZoneInfo("Asia/Kolkata"))
        
        updated = await crud.update_appointment_window(
            session, 
            request.appointment_id, 
            dt_ist, 
            request.window
        )
        return {"status": "success", "data": updated}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# from fastapi import APIRouter, Depends, HTTPException
# from sqlmodel import Session
# from ..database import get_session
# from .. import crud, models
# from datetime import datetime
# from zoneinfo import ZoneInfo

# router = APIRouter(prefix="/scheduling", tags=["Scheduling"])

# @router.get("/lead/{lead_id}")
# def get_lead_status(lead_id: str, session: Session = Depends(get_session)):
#     # Used in Frontend to check who the user is
#     appointment = crud.get_appointment_by_lead(session, lead_id)
#     if not appointment:
#         raise HTTPException(status_code=404, detail="No appointment found")
#     return appointment

# @router.post("/select-window")
# def select_window(
#     appointment_id: str, 
#     date_str: str, 
#     window: models.TimeWindow, 
#     session: Session = Depends(get_session)
# ):
#     try:
#         dt_naive = datetime.strptime(date_str, "%Y-%m-%d")
        
#         dt_ist = dt_naive.replace(tzinfo=ZoneInfo("Asia/Kolkata"))
        
#         updated = crud.update_appointment_window(session, appointment_id, dt_ist, window)
#         return {"status": "success", "data": updated}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
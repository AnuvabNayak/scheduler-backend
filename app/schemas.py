from pydantic import BaseModel
from .models import TimeWindow

class WindowSelectionRequest(BaseModel):
    appointment_id: str
    date_str: str # Format YYYY-MM-DD
    window: TimeWindow
from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks, Header
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_session
from .. import crud
import os
import httpx
import hmac
import hashlib

router = APIRouter(tags=["Webhook"])

# Config
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_API_TOKEN")
PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
APP_SECRET = os.getenv("WHATSAPP_APP_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# --- SECURITY UTILS ---
async def verify_signature(request: Request):
    """Verifies that the request actually came from Meta"""
    if not APP_SECRET:
        return # Skip if secret not set (Dev mode)
        
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        raise HTTPException(403, "Missing Signature")
        
    body = await request.body()
    expected = hmac.new(APP_SECRET.encode(), body, hashlib.sha256).hexdigest()
    
    if not hmac.compare_digest(f"sha256={expected}", signature):
        raise HTTPException(403, "Invalid Signature")

# --- 1. VERIFICATION ---
@router.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    if params.get("hub.verify_token") == VERIFY_TOKEN:
        return int(params.get("hub.challenge"))
    raise HTTPException(status_code=403, detail="Invalid verification token")

# --- 2. EVENT LISTENER ---
@router.post("/webhook")
async def receive_whatsapp_event(
    request: Request, 
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session)
):
    # 1. Verify Security
    await verify_signature(request)
    
    # 2. Parse Data
    data = await request.json()
    
    if data.get("object") == "whatsapp_business_account":
        try:
            entry = data["entry"][0]
            changes = entry["changes"][0]
            value = changes["value"]
            
            if "messages" in value:
                message = value["messages"][0]
                sender_phone = message["from"]
                
                if message.get("type") == "text":
                    # Pass the session to background task? 
                    # NO. Async Sessions cannot be shared across threads easily.
                    # We must run the logic HERE and await it, 
                    # OR create a new session in the background task.
                    # For simplicity in FastAPI, we await logic here. 
                    # (To optimize, we would use a task queue like Celery).
                    
                    await handle_new_message(sender_phone, session)
                    
        except (KeyError, IndexError):
            pass

    return {"status": "received"}

# --- 3. BUSINESS LOGIC ---
async def handle_new_message(phone: str, session: AsyncSession):
    # 1. Check Lead
    lead = await crud.get_lead_by_phone(session, phone)
    
    if not lead:
        lead = await crud.create_lead(session, phone)
    
    # 2. Check for Open Appointment (Fixes Double Booking)
    existing_appt = await crud.get_open_appointment(session, lead.id)
    
    if existing_appt:
        link = f"{FRONTEND_URL}/book/{lead.id}"
        await send_whatsapp_message(
            phone, 
            f"You have an open request. Resume booking here: {link}"
        )
    else:
        # Create new
        new_appt = await crud.create_initial_appointment(session, lead.id)
        link = f"{FRONTEND_URL}/book/{lead.id}"
        await send_whatsapp_message(
            phone, 
            f"Hi! Tap here to schedule your call: {link}"
        )

# --- 4. OUTBOUND UTILS ---
async def send_whatsapp_message(to_phone: str, text: str):
    if not WHATSAPP_TOKEN: return
    
    url = f"https://graph.facebook.com/v17.0/{PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "text",
        "text": {"body": text}
    }
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload, headers=headers)
        

from contextlib import asynccontextmanager
from fastapi import FastAPI
from .database import init_db
from .routers import scheduling, webhook

@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Startup: Connecting to Database and creating tables...")
    await init_db()
    
    yield
    
    print("Shutdown: Cleaning up resources...")

app = FastAPI(
    title="WhatsApp Scheduler API",
    lifespan=lifespan
)

# Include Routers
app.include_router(scheduling.router)
app.include_router(webhook.router)

@app.get("/")
def home():
    return {"message": "Scheduler Backend Running", "status": "Live"}
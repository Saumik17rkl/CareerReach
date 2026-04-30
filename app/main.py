import os
from fastapi import FastAPI
from app.database import Base, engine
from app.routers import contacts, upload, submit, stats
from app.health import router as health_router

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="ReachBridge API",
    description="Backend system for processing HR and company contact data",
    version="1.0.0"
)

# Include routers
app.include_router(contacts.router)
app.include_router(upload.router)
app.include_router(submit.router)
app.include_router(stats.router)
app.include_router(health_router)

@app.get("/")
def root():
    return {
        "message": "ReachBridge API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }
import os
import sys
from pathlib import Path

# Add current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI(
    title="CareerReach API",
    description="Backend system for processing HR and company contact data",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Try to use MongoDB first
database_type = "Minimal Mode"


def _include_in_memory_fallback_routers() -> None:
    global database_type
    from routers.mongodb_contacts_simple import router as contacts_router
    from routers.mongodb_upload_simple import router as upload_router
    from routers.mongodb_submit_simple import router as submit_router
    from health_simple import router as health_router

    database_type = "In-Memory Fallback"
    app.include_router(contacts_router)
    app.include_router(upload_router)
    app.include_router(submit_router)
    app.include_router(health_router)


def _include_mongodb_routers() -> None:
    global database_type
    from routers.mongodb_contacts_fixed import router as contacts_router
    from routers.mongodb_upload_fixed import router as upload_router
    from routers.mongodb_submit_fixed import router as submit_router
    from health_simple import router as health_router

    database_type = "MongoDB Atlas"
    app.include_router(contacts_router)
    app.include_router(upload_router)
    app.include_router(submit_router)
    app.include_router(health_router)


try:
    # Single source of truth for Mongo configuration
    from mongodb_fixed import test_connection

    if test_connection():
        _include_mongodb_routers()
        print("✅ MongoDB connected successfully")
    else:
        _include_in_memory_fallback_routers()
except Exception as e:
    print(f"⚠️ MongoDB not available: {e}")
    _include_in_memory_fallback_routers()

# Add basic endpoints for all modes
@app.get("/")
def root():
    return {
        "message": "CareerReach API",
        "version": "2.0.0",
        "database": database_type,
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CareerReach API",
        "version": "2.0.0",
        "database": database_type
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mongodb import test_connection
from routers import mongodb_contacts, mongodb_upload, mongodb_submit
from health import router as health_router

# Initialize FastAPI app
app = FastAPI(
    title="CareerReach API",
    description="Backend system for processing HR and company contact data with MongoDB",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(mongodb_contacts.router)
app.include_router(mongodb_upload.router)
app.include_router(mongodb_submit.router)
app.include_router(health_router)

@app.on_event("startup")
async def startup_event():
    # Test MongoDB connection
    if test_connection():
        print("✅ MongoDB connection established")
    else:
        print("❌ MongoDB connection failed")

@app.get("/")
async def root():
    return {
        "message": "CareerReach API with MongoDB",
        "version": "2.0.0",
        "database": "MongoDB Atlas"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.mongodb_contacts_simple import router as contacts_router
from routers.mongodb_upload_simple import router as upload_router
from routers.mongodb_submit_simple import router as submit_router
from health_simple import router as health_router

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
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(contacts_router)
app.include_router(upload_router)
app.include_router(submit_router)
app.include_router(health_router)

@app.on_event("startup")
async def startup_event():
    print("✅ CareerReach API started successfully")
    print("📝 Note: Running with in-memory storage for testing")
    print("🔄 Data will persist across requests but not server restarts")

@app.get("/")
async def root():
    return {
        "message": "CareerReach API",
        "version": "2.0.0",
        "database": "In-Memory (Testing Mode)",
        "note": "This is a working version for testing. MongoDB setup coming soon."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

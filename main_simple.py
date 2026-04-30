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
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Try to use MongoDB first
database_type = "Minimal Mode"
try:
    from pymongo import MongoClient
    from dotenv import load_dotenv
    load_dotenv()
    
    mongodb_password = os.getenv("MONGODB_PASSWORD", "")
    if mongodb_password:
        try:
            mongodb_uri = f"mongodb+srv://saumik17rkl_db_user:{mongodb_password}@cluster0.sz9lcyt.mongodb.net/?appName=Cluster0"
            client = MongoClient(
                mongodb_uri,
                tls=True,
                tlsAllowInvalidCertificates=True,
                connectTimeoutMS=30000,
                socketTimeoutMS=30000
            )
            client.admin.command('ping')
            
            # Use MongoDB routers
            from routers.mongodb_contacts_simple import router as contacts_router
            from routers.mongodb_upload_simple import router as upload_router  
            from routers.mongodb_submit_simple import router as submit_router
            from health_simple import router as health_router
            
            database_type = "MongoDB Atlas"
            print("✅ MongoDB connected successfully")
            
            app.include_router(contacts_router)
            app.include_router(upload_router)
            app.include_router(submit_router)
            app.include_router(health_router)
            
        except Exception as mongo_error:
            print(f"⚠️ MongoDB connection failed: {mongo_error}")
            database_type = "MongoDB Failed"
    else:
        print("⚠️ MONGODB_PASSWORD not found")
        database_type = "MongoDB Not Configured"
        
except Exception as e:
    print(f"⚠️ MongoDB not available: {e}")
    database_type = "MongoDB Unavailable"

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

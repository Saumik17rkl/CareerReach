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
    allow_origins=["*"],  # Allow all origins for frontend access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Try to use MongoDB first, fallback to SQLite
database_type = "SQLite"
try:
    # Try MongoDB imports
    from pymongo import MongoClient
    from dotenv import load_dotenv
    load_dotenv()
    
    # MongoDB connection
    mongodb_password = os.getenv("MONGODB_PASSWORD", "")
    if mongodb_password:
        try:
            mongodb_uri = f"mongodb+srv://saumik17rkl_db_user:{mongodb_password}@cluster0.sz9lcyt.mongodb.net/?appName=Cluster0"
            client = MongoClient(mongodb_uri)
            client.admin.command('ping')  # Test connection
            
            # Use MongoDB routers (simple versions that work)
            from routers.mongodb_contacts_simple import router as contacts_router
            from routers.mongodb_upload_simple import router as upload_router  
            from routers.mongodb_submit_simple import router as submit_router
            from health_simple import router as health_router
            
            database_type = "MongoDB Atlas"
            print("✅ MongoDB connected successfully")
            
            # Include MongoDB routers
            app.include_router(contacts_router)
            app.include_router(upload_router)
            app.include_router(submit_router)
            app.include_router(health_router)
            
        except Exception as mongo_error:
            print(f"⚠️ MongoDB connection failed: {mongo_error}")
            print("🔄 Using SQLite fallback...")
            raise Exception("MongoDB unavailable")
    else:
        print("⚠️ MONGODB_PASSWORD not found")
        print("🔄 Using SQLite fallback...")
        raise Exception("MongoDB password not set")
        
except Exception as e:
    print(f"⚠️ MongoDB not available: {e}")
    print("🔄 Using SQLite fallback...")
    
    # SQLite fallback
    try:
        from database import Base, engine
        Base.metadata.create_all(bind=engine)
        
        # Use SQLite routers
        from routers import contacts, upload, submit, stats
        from health import router as health_router
        
        database_type = "SQLite"
        print("✅ SQLite fallback activated")
        
        # Include SQLite routers
        app.include_router(contacts.router)
        app.include_router(upload.router)
        app.include_router(submit.router)
        app.include_router(stats.router)
        app.include_router(health_router)
        
    except Exception as sqlite_error:
        print(f"❌ SQLite fallback also failed: {sqlite_error}")
        print("🚨 No database available - running in minimal mode")

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

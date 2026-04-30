import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://saumik17rkl_db_user:<password>@cluster0.sz9lcyt.mongodb.net/?appName=Cluster0")
DB_NAME = "CareerReach"

# Replace <password> with actual password from environment
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD", "")
if MONGODB_PASSWORD:
    MONGODB_URI = MONGODB_URI.replace("<password>", MONGODB_PASSWORD)

# MongoDB client
try:
    from pymongo import MongoClient
    client = MongoClient(MONGODB_URI)
    db = client[DB_NAME]
    
    # Collections
    contacts_collection = db["contacts"]
    access_logs_collection = db["access_logs"]
    
    def get_mongodb():
        """Get MongoDB database instance"""
        return db
    
    def test_connection():
        """Test MongoDB connection"""
        try:
            client.admin.command('ping')
            print("MongoDB connection successful!")
            return True
        except Exception as e:
            print(f"MongoDB connection failed: {e}")
            return False
            
except ImportError as e:
    print(f"MongoDB import failed: {e}")
    print("Please install: pip install pymongo")
    client = None
    db = None
    contacts_collection = None
    access_logs_collection = None
    
    def get_mongodb():
        return None
    
    def test_connection():
        return False

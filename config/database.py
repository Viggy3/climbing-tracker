import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv
from pymongo.database import Database
from typing import Generator

# Load environment variables from .env file
load_dotenv()

# Get MongoDB connection details from environment variables
MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME", "ClimbingApp")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "climbing_app_collection")

if not MONGODB_URL:
    raise ValueError("MONGODB_URL environment variable is not set")
uri = MONGODB_URL
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))



# Get database and collections
db = client[DATABASE_NAME]
trackers_collection = db[COLLECTION_NAME]  # Fixed: renamed from collection_name to collection
users_collection = db["users"]  # Collection for user authentication data



def test_connection():
    """Test the MongoDB connection"""
    try:
        # The ping command is cheap and does not require auth
        client.admin.command('ping')
        print(f"✓ Successfully connected to MongoDB!")
        print(f"✓ Database: {DATABASE_NAME}")
        print(f"✓ Collection: {COLLECTION_NAME}")
        return True
    except ConnectionFailure:
        print("✗ Failed to connect to MongoDB. Please check your connection string.")
        return False
    except ServerSelectionTimeoutError:
        print("✗ MongoDB server selection timeout. Is your MongoDB instance running?")
        return False
    except Exception as e:
        print(f"✗ An error occurred: {e}")
        return False

def check_user_exists(user_info):
    """Check if a user already exists in the database based on Google sub or email"""
    google_sub = user_info.get("sub")
    email = user_info.get("email")
    existing_user = users_collection.find_one({"$or": [{"google_sub": google_sub}, {"email": email}]})
    return existing_user

def update_user_login(user_id):
    """Update the last_login timestamp for an existing user"""
    from datetime import datetime
    users_collection.update_one(
        {"_id": user_id},
        {"$set": {"last_login": datetime.now()}}
    )   


# Optional: Test connection when module is imported
if __name__ == "__main__":
    test_connection()
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get MongoDB connection details from environment variables
MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME", "ClimbingApp")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "climbing_app_collection")

if not MONGODB_URL:
    raise ValueError("MONGODB_URL environment variable is not set")

# Create MongoDB client
client = MongoClient(MONGODB_URL)

# Get database and collection
db = client[DATABASE_NAME]
collection_name = db[COLLECTION_NAME]

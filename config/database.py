import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

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


# Create MongoDB client with timeout settings
# client = MongoClient(
#     MONGODB_URL,
#     serverSelectionTimeoutMS=5000,  # 5 second timeout
#     connectTimeoutMS=10000,  # 10 second connection timeout
#     server_api = ServerApi('1'),
#     tls=True
# )

# Get database and collection
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]  # Fixed: renamed from collection_name to collection


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


# Optional: Test connection when module is imported
if __name__ == "__main__":
    test_connection()
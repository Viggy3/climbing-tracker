"""
Test script for database.py configuration
Run this to verify your MongoDB connection is working properly
"""

from database import client, db, collection, test_connection

def main():
    print("=" * 50)
    print("Testing MongoDB Connection")
    print("=" * 50)
    
    # Test connection
    if test_connection():
        print("\n" + "=" * 50)
        print("Running Additional Tests")
        print("=" * 50)
        
        # Try to insert a test document
        try:
            test_doc = {"test": "connection_test", "status": "success"}
            result = collection.insert_one(test_doc)
            print(f"✓ Successfully inserted test document with ID: {result.inserted_id}")
            
            # Try to find the document
            found_doc = collection.find_one({"_id": result.inserted_id})
            print(f"✓ Successfully retrieved test document: {found_doc}")
            
            # Clean up - delete the test document
            collection.delete_one({"_id": result.inserted_id})
            print(f"✓ Successfully deleted test document")
            
            print("\n" + "=" * 50)
            print("All tests passed! Your database is ready to use.")
            print("=" * 50)
            
        except Exception as e:
            print(f"✗ Error during testing: {e}")
            print("Note: Make sure your MongoDB user has read/write permissions")
    else:
        print("\n" + "=" * 50)
        print("Connection test failed. Please check:")
        print("1. Is your .env file configured correctly?")
        print("2. Is your MongoDB instance running?")
        print("3. Is your connection string correct?")
        print("4. Do you have network access to the MongoDB server?")
        print("=" * 50)

if __name__ == "__main__":
    main()
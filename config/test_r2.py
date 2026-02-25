from database import media_collection  # or wherever media docs live

for doc in media_collection.find():
    updates = {}
    if doc.get("key", "").startswith("media/"):
        updates["key"] = doc["key"][6:]  # remove "media/"
    if (doc.get("thumbnail") or "").startswith("media/"):
        updates["thumbnail"] = doc["thumbnail"][6:]
    if updates:
        media_collection.update_one({"_id": doc["_id"]}, {"$set": updates})
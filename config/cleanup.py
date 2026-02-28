from datetime import datetime, timedelta, timezone
from config.database import media_collection, pending_uploads_collection
from config.r2_storage import delete_from_r2


async def cleanup_orphaned_uploads():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
    orphaned_uploads = list(pending_uploads_collection.find({"created_at": {"$lt": cutoff}}))
    for upload in orphaned_uploads:
        real_doc = media_collection.find_one({"key": upload["key"]})
        if not real_doc:
            delete_from_r2(upload["key"])
            pending_uploads_collection.delete_one({"_id": upload["_id"]})
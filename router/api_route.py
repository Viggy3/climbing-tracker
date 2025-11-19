from config.r2_storage import upload_to_storage, delete_from_r2
import token
import uuid
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.config import Config
from authlib.integrations.starlette_client import OAuth
from starlette.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path
from config.database import users_collection, update_user_login, check_user_exists, trackers_collection, media_collection
import os
import python_multipart
from bson import ObjectId
#adding template pointer
templates = Jinja2Templates(directory="templates")

api_router = APIRouter()

#display page for creating new tracker
@api_router.get("/new_tracker")
async def new_tracker_page(request: Request):
    return templates.TemplateResponse("new_tracker.html", {"request": request})

# POST request to add a new tracker
@api_router.post("/create_tracker")
async def create_tracker(request: Request):
    try:
        # Get form data instead of JSON
        form_data = await request.form()
        
        # Extract user_id from session
        user_id = request.session.get('user_id')
        if not user_id:
            return RedirectResponse(url="/auth/login", status_code=302)
        
        # Create tracker data from form
        user_description = form_data.get("description", "").strip()
        
        # Combine grade info with user notes
        if user_description:
            full_description = user_description
        else:
            full_description = "No additional notes."
        
        tracker_id = ObjectId()
        
        tracker_data = {
            "name": form_data.get("climb_name"),
            "description": full_description,
            "date": form_data.get("date"),
            "attempts": form_data.get("attempts", 1),  # Default to 1 attempt for new climb
            "grade": form_data.get("grade"),
            "complete": form_data.get("complete", False),  # Default to incomplete
            "user_id": user_id,  # Link to authenticated user
            "_id": tracker_id
        }

        media_files = form_data.getlist("media_files")
        print(f"🔍 Found {len(media_files)} media files")
        if media_files:
            media_ids = []
            for media_file in media_files:
                if media_file.filename:
                    print(f"📁 Processing file: {media_file.filename}")
                    # Read file content first
                    file_content = await media_file.read()
                    file_size = len(file_content)
                    
                    # Reset file pointer for upload function
                    media_file.file.seek(0)
                    file_extension = os.path.splitext(media_file.filename)[1]
                    unique_filename = f"{user_id}/{tracker_id}/{uuid.uuid4()}{file_extension}"
                    file_url = upload_to_storage(media_file, tracker_id, user_id, unique_filename=unique_filename)
                    
                    if file_url:  # Only process if upload was successful
                        print(f"📤 Uploaded to: {file_url}")
                        
                        # Create media document
                        media_doc = {
                            "filename": media_file.filename,
                            "key": file_url,
                            "mime": media_file.content_type,
                            "size": file_size,
                            "status": "uploaded",
                            "tracker_id": str(tracker_id)  # Convert ObjectId to string
                        }

                        media_result = media_collection.insert_one(media_doc)
                        print(f"💾 Saved media doc: {media_result.inserted_id}")
                        media_ids.append(media_result.inserted_id)
                    else:
                        print(f"❌ Skipping file {media_file.filename} - upload failed")
            tracker_data["media_ids"] = media_ids

        
        # Import here to avoid circular imports
        from config.database import trackers_collection
        from datetime import datetime, timezone
        
        # Convert date string to datetime if provided
        if tracker_data["date"]:
            tracker_data["date"] = datetime.fromisoformat(tracker_data["date"])
        else:
            tracker_data["date"] = datetime.now(timezone.utc)
        
        # Insert into database
        result = trackers_collection.insert_one(tracker_data)
        # Redirect to user dashboard
        return RedirectResponse(url="/user/my_tracker", status_code=302)
        
    except Exception as e:
        print(f" Error creating tracker: {e}")
        # Return to form with error
        return templates.TemplateResponse(
            "new_tracker.html", 
            {"request": request, "error": "Failed to create tracker. Please try again."}
        )

# Additional API routes can be added here
@api_router.get("/edit_tracker/{tracker_id}")
async def edit_tracker(tracker_id: str, request: Request):
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            return RedirectResponse(url="/auth/login", status_code=302)
        from config.database import trackers_collection
        climb_data = trackers_collection.find_one({"_id": ObjectId(tracker_id), "user_id": user_id})
        if not climb_data:
            print(" Climb not found or access denied.") 
            return RedirectResponse(url="/user/my_tracker", status_code=302)
        media_docs = list(media_collection.find({"tracker_id": tracker_id}))  # tracker_id is stored as string
        print(f"Found {len(media_docs)} media files for tracker {tracker_id}")
    
        for doc in media_docs:
            doc["url"] = f"https://{doc['key']}"
        context = {
            "request": request,
            "climb": climb_data,
            "media_files": media_docs,  # Template expects 'media_files'
            "has_media": len(media_docs) > 0
        }
        return templates.TemplateResponse("climb_details.html", context)
    except Exception as e:
        print(f" Error editing tracker: {e}")
        return RedirectResponse(url="/user/my_tracker", status_code=302)
    

@api_router.post("/update_tracker/{tracker_id}")
async def update_tracker(tracker_id: str, request: Request):

    try:
        form_data = await request.form()

        user_id = request.session.get('user_id')
        if not user_id:
            return RedirectResponse(url="/auth/login", status_code=302)
        from config.database import trackers_collection
        from datetime import datetime
        media_ids = trackers_collection.find_one({"_id": ObjectId(tracker_id), "user_id": user_id}).get("media_ids", [])
        update_data = {
            "description": form_data.get("edit_climb_description", "").strip(),
            "attempts": int(form_data.get("edit_climb_attempts", 1)),
            "grade": form_data.get("edit_climb_grade"),
            "complete": form_data.get("edit_climb_complete") == "on",
            "media_ids": media_ids,
        }
        media_files = form_data.getlist("media_files")
        print(f"Found {len(media_files)} media files to upload")
        
        # Get existing media keys with error handling
        try:
            existing_media_keys = {doc["key"] for doc in media_collection.find({"tracker_id": tracker_id}, {"key": 1})}
            print(f" {len(existing_media_keys)} existing media files ")
        except Exception as e:
            print(f"Error fetching existing media keys: {e}")
            existing_media_keys = set()  # Continue with empty set
        
        # Process each media file with individual error handling
        successful_uploads = 0
        failed_uploads = 0
        print(f"Total media_files received: {len(media_files)}")
        for i, media in enumerate(media_files):
            print(f"Processing media file #{i}: {media}")
            print(f"Filename: '{media.filename}' (type: {type(media.filename)})")
            print(f"Content type: {getattr(media, 'content_type', 'None')}")
            
            # More specific check for empty files
            if not media.filename or media.filename.strip() == "":
                print(f" Skipping empty file entry #{i}")
                continue
                
            try:
                print(f" Processing file: {media.filename}")

                # Generate unique filename and worker URL
                file_extension = os.path.splitext(media.filename)[1]
                unique_filename = f"{user_id}/{tracker_id}/{uuid.uuid4()}{file_extension}"
                worker_url = f"tracker-media-proxy.hariviggy333.workers.dev/media/{unique_filename}"
                duplicate_check = f"{media.filename}_{file_size}"
                existing_files = {f"{doc['filename']}_{doc['size']}" for doc in media_collection.find({"tracker_id": tracker_id})}
                if duplicate_check in existing_files:
                    print(f"Duplicate file detected: {media.filename}")
                    continue
                

                # Read file content and reset pointer
                try:
                    file_content = await media.read()
                    file_size = len(file_content)
                    media.file.seek(0)
                except Exception as read_error:
                    print(f"Error reading file {media.filename}: {read_error}")
                    failed_uploads += 1
                    continue

                # Upload to R2
                try:
                    file_url = upload_to_storage(media, tracker_id, user_id, unique_filename=unique_filename)
                except Exception as upload_error:
                    print(f"Upload failed for {media.filename}: {upload_error}")
                    failed_uploads += 1
                    continue

                if file_url:
                    try:
                        # Create and save media document
                        media_doc = {
                            "filename": media.filename,
                            "key": file_url,
                            "mime": media.content_type,
                            "size": file_size,
                            "status": "uploaded",
                            "tracker_id": str(tracker_id)
                        }

                        media_result = media_collection.insert_one(media_doc)
                        media_ids.append(media_result.inserted_id)
                        successful_uploads += 1
                        print(f"Successfully processed: {media.filename}")
                        
                    except Exception as db_error:
                        print(f"Database save failed for {media.filename}: {db_error}")
                        failed_uploads += 1
                else:
                    print(f"Upload returned no URL for {media.filename}")
                    failed_uploads += 1
                    
            except Exception as e:
                print(f"Unexpected error processing {media.filename}: {e}")
                failed_uploads += 1
                continue
        
        print(f"Media processing complete: {successful_uploads} successful, {failed_uploads} failed")
                    

        print(form_data.items())
        trackers_collection.update_one(
            {"_id": ObjectId(tracker_id), "user_id": user_id},
            {"$set": update_data}
        )

        return RedirectResponse(url="/user/my_tracker", status_code=302)
    except Exception as e:
        print(f"error updating database climb {tracker_id}: {e}")
        return RedirectResponse(url="/user/my_tracker", status_code=302)


@api_router.get("/view_climb/{tracker_id}")
async def view_climb(tracker_id: str, request: Request):
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            return RedirectResponse(url="/auth/login", status_code=302)
        from config.database import trackers_collection
        climb_data = trackers_collection.find_one({"_id": ObjectId(tracker_id), "user_id": user_id})
        if not climb_data:
            print(" Climb not found or access denied.") 
            return RedirectResponse(url="/user/my_tracker", status_code=302)
        
        media_url_prefix = os.getenv("CLOUDFLARE_R2_MEDIAURL", "")



        media_docs = list(media_collection.find({"tracker_id": tracker_id}))  # tracker_id is stored as string
        print(f"Found {len(media_docs)} media files for tracker {tracker_id}")
    
        for doc in media_docs:
            doc["url"] = f"https://{doc['key']}"

        context = {
            "request": request,
            "climb": climb_data,
            "media_files": media_docs,  # Template expects 'media_files'
            "has_media": len(media_docs) > 0
        }
        return templates.TemplateResponse("view_climb.html", context)
    except Exception as e:
        print(f" Error viewing tracker: {e}")
        return RedirectResponse(url="/user/my_tracker", status_code=302)
    
@api_router.delete("/delete_media/{media_id}")
async def delete_media(media_id: str, request: Request):
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            return RedirectResponse(url="/auth/login", status_code=302)
        
        media_doc = media_collection.find_one({"_id": ObjectId(media_id)})
        if not media_doc:
            print(" Media not found.") 
            return RedirectResponse(url="/user/my_tracker", status_code=302)
        
        tracker_id = media_doc.get("tracker_id")
        tracker_doc = trackers_collection.find_one({"_id": ObjectId(tracker_id), "user_id": user_id})
        if not tracker_doc:
            print(" Access denied to delete media.") 
            return RedirectResponse(url="/user/my_tracker", status_code=302)
        success = delete_from_r2(media_doc["key"])
        if success:
            media_collection.delete_one({"_id": ObjectId(media_id)})
            trackers_collection.update_one(
                {"_id": ObjectId(tracker_id)},
                {"$pull": {"media_ids": ObjectId(media_id)}}
            )
            print(f" Deleted media {media_id} successfully.")
            
            return {"success": True}
        else:
            print(" Failed to delete media from R2.") 
            return {"success": False}
        
    except Exception as e:
        print(f" Error deleting media: {e}")
        return {"error" : str(e), "success": False}, 500

@api_router.delete("/delete_tracker/{tracker_id}")
async def delete_tracker(tracker_id: str, request: Request):
    print(f" Received request to delete tracker {tracker_id}")
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            return RedirectResponse(url="/auth/login", status_code=302)
        
        tracker_doc = trackers_collection.find_one({"_id": ObjectId(tracker_id), "user_id": user_id})
        if not tracker_doc:
            print(" Tracker not found or access denied.") 
            return RedirectResponse(url="/user/my_tracker", status_code=302)
        
        media_docs = list(media_collection.find({"tracker_id": tracker_id}))
        for media_doc in media_docs:
            success = delete_from_r2(media_doc["key"])
            if success:
                media_collection.delete_one({"_id": media_doc["_id"]})
                print(f" Deleted media {media_doc['_id']} successfully.")
            else:
                print(f" Failed to delete media {media_doc['_id']} from R2.") 

        trackers_collection.delete_one({"_id": ObjectId(tracker_id)})
        print(f" Deleted tracker {tracker_id} successfully.")
        
        return {"success": True}
    except Exception as e:
        print(f" Error deleting tracker: {e}")
        return {"error" : str(e), "success": False}, 500
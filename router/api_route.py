from config.r2_storage import generate_thumbnail, get_r2, upload_to_storage, delete_from_r2
import token
import hmac
import hashlib
from datetime import datetime, timezone, timedelta
from urllib.parse import quote
import uuid
from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import RedirectResponse, JSONResponse
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
async def create_tracker(request: Request, background_tasks: BackgroundTasks):
    try:
        user_id = request.session.get('user_id')

        if not user_id:
            return RedirectResponse(url="/auth/login", status_code=302)
        body = await request.json()
        user_description = body.get("description", "").strip() or "No additional notes."
        tracker_id = ObjectId(body.get("tracker_id"))


        tracker_data = {
            "_id": tracker_id,
            "name": body.get("climb_name"),
            "description": user_description,
            "attempts": body.get("attempts", 1),
            "grade": body.get("grade"),
            "complete": body.get("complete", False),
            "user_id": user_id,
        }

        media_ids=[]
        for media in body.get("media_files", []):
            worker_url = f"tracker-media-proxy.hariviggy333.workers.dev/media/{media['key']}"
            thumbnail_url = None
            
            media_doc = {
                "filename": media["filename"],
                "key": worker_url,
                "mime": media["content_type"],
                "size": media["size"],
                "status": "uploaded",
                "tracker_id": str(tracker_id),
                "thumbnail": thumbnail_url 
            }

            result = media_collection.insert_one(media_doc)
            media_ids.append(result.inserted_id)

            if media["content_type"].startswith("video/"):
                background_tasks.add_task(generate_and_save_thumbnail, media["key"], user_id, str(tracker_id), result.inserted_id)
            
        
        if media_ids:
            tracker_data["media_ids"] = media_ids

        from config.database import trackers_collection
        from datetime import datetime, timezone

        date_str = body.get("date")
        tracker_data["date"] = datetime.fromisoformat(date_str) if date_str else datetime.now(timezone.utc)

        trackers_collection.insert_one(tracker_data)

        return JSONResponse({"success": True, "tracker_id": str(tracker_id)})
    except Exception as e:
        print(f"Error creating tracker: {e}")
        return JSONResponse({"error": "Failed to create tracker."}, status_code=500)

def generate_and_save_thumbnail(video_key, user_id, tracker_id, media_id):
    thumbnail_url = generate_thumbnail(video_key, user_id, tracker_id)
    if thumbnail_url:
        media_collection.update_one(
            {"_id": media_id},
            {"$set": {"thumbnail": thumbnail_url}}
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
        user_id = request.session.get('user_id')
        if not user_id:
            return JSONResponse({"error": "Not authenticated"}, status_code=401)

        body = await request.json()

        from config.database import trackers_collection
        
        # Get existing media_ids to preserve them
        existing = trackers_collection.find_one({"_id": ObjectId(tracker_id), "user_id": user_id})
        if not existing:
            return JSONResponse({"error": "Tracker not found"}, status_code=404)

        media_ids = existing.get("media_ids", [])

        # Save any newly uploaded media metadata
        for media in body.get("media_files", []):
            worker_url = f"tracker-media-proxy.hariviggy333.workers.dev/media/{media['key']}"

            thumbnail_url = None
            if media["content_type"].startswith("video/"):
                thumbnail_url = generate_thumbnail(media["key"], user_id, str(tracker_id))
            media_doc = {
                "filename": media["filename"],
                "key": worker_url,
                "mime": media["content_type"],
                "size": media["size"],
                "status": "uploaded",
                "tracker_id": tracker_id,
                "thumbnail": thumbnail_url
            }
            result = media_collection.insert_one(media_doc)
            media_ids.append(result.inserted_id)

        update_data = {
            "grade": body.get("edit_climb_grade"),
            "description": body.get("edit_climb_description", "").strip() or "No additional notes.",
            "attempts": int(body.get("edit_climb_attempts", 1)),
            "complete": body.get("edit_climb_complete", False),
            "media_ids": media_ids,
        }

        trackers_collection.update_one(
            {"_id": ObjectId(tracker_id), "user_id": user_id},
            {"$set": update_data}
        )

        return JSONResponse({"success": True})

    except Exception as e:
        print(f"Error updating tracker {tracker_id}: {e}")
        return JSONResponse({"error": "Failed to update tracker."}, status_code=500)


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
    
@api_router.get("/new_tracker_id")
async def new_tracker_id(request: Request):
    user_id = request.session.get('user_id')
    if not user_id:
        return RedirectResponse(url="/auth/login", status_code=302)
    return {"tracker_id": str(ObjectId())}

@api_router.post("/get_upload_url")
async def get_upload_url(request: Request):
    user_id = request.session.get('user_id')
    if not user_id:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)

    body = await request.json()
    filename = body.get("filename")
    content_type = body.get("content_type")
    tracker_id = body.get("tracker_id")

    file_extension = os.path.splitext(filename)[1]
    unique_key = f"{user_id}/{tracker_id}/{uuid.uuid4()}{file_extension}"

    account_id = os.getenv('CLOUDFLARE_R2_ACCOUNT_ID')
    access_key = os.getenv("CLOUDFLARE_R2_ACCESS_KEY_ID")
    secret_key = os.getenv("CLOUDFLARE_R2_SECRET_ACCESS_KEY")
    bucket_name = os.getenv("CLOUDFLARE_R2_BUCKET_NAME")

    host = f"{bucket_name}.{account_id}.r2.cloudflarestorage.com"
    now = datetime.now(timezone.utc)
    datestamp = now.strftime('%Y%m%d')
    amzdate = now.strftime('%Y%m%dT%H%M%SZ')
    expires = 3600

    credential_scope = f"{datestamp}/auto/s3/aws4_request"
    credential = f"{access_key}/{credential_scope}"

    signed_headers = "content-type;host"

    canonical_querystring = (
        f"X-Amz-Algorithm=AWS4-HMAC-SHA256"
        f"&X-Amz-Credential={quote(credential, safe='')}"
        f"&X-Amz-Date={amzdate}"
        f"&X-Amz-Expires={expires}"
        f"&X-Amz-SignedHeaders={quote(signed_headers, safe='')}"
    )

    canonical_headers = f"content-type:{content_type}\nhost:{host}\n"
    canonical_request = "\n".join([
        "PUT",
        f"/{unique_key}",
        canonical_querystring,
        canonical_headers,
        signed_headers,
        "UNSIGNED-PAYLOAD"
    ])

    string_to_sign = "\n".join([
        "AWS4-HMAC-SHA256",
        amzdate,
        credential_scope,
        hashlib.sha256(canonical_request.encode()).hexdigest()
    ])

    def sign(key, msg):
        return hmac.new(key, msg.encode(), hashlib.sha256).digest()

    signing_key = sign(sign(sign(sign(f"AWS4{secret_key}".encode(), datestamp), "auto"), "s3"), "aws4_request")
    signature = hmac.new(signing_key, string_to_sign.encode(), hashlib.sha256).hexdigest()

    presigned_url = (
        f"https://{host}/{unique_key}"
        f"?{canonical_querystring}"
        f"&X-Amz-Signature={signature}"
    )
    print(f"Generated presigned URL: {presigned_url}")

    return JSONResponse({"upload_url": presigned_url, "key": unique_key})


@api_router.get("/check_ffmpeg")
async def check_ffmpeg(request: Request):
    try:
        import imageio_ffmpeg
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        return JSONResponse({"available": True, "path": ffmpeg_path})
    except Exception as e:
        return JSONResponse({"available": False, "error": str(e)})
from datetime import datetime, timezone

import shutil
from pathlib import Path

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File

from app.database import db
from app.schemas.request import CreateRequest
from app.schemas.comment import CreateComment
from app.utils.auth import get_current_user


router = APIRouter(
    prefix="/requests",
    tags=["Service Requests"]
)


# ---------------------------------------------------------
# CREATE SERVICE REQUEST
# ---------------------------------------------------------

@router.post("/")
async def create_request(
    data: CreateRequest,
    current_user: dict = Depends(get_current_user)
):
    now = datetime.now(timezone.utc)

    request_count = await db.service_requests.count_documents({}) + 1

    request_no = f"REQ-2026-{request_count:04d}"

    request = {
        "request_no": request_no,
        "title": data.title,
        "description": data.description,
        "category": data.category,
        "priority": data.priority,
        "status": "NEW",
        "department_id": current_user["department_id"],
        "created_by": current_user["sub"],
        "assigned_to": None,
        "created_at": now,
        "updated_at": now,
        "resolved_at": None,
        "closed_at": None
    }

    result = await db.service_requests.insert_one(request)

    return {
        "message": "Request created successfully",
        "request_id": str(result.inserted_id),
        "request_no": request_no
    }


# ---------------------------------------------------------
# GET ALL REQUESTS FOR LOGGED-IN USER'S DEPARTMENT
# ---------------------------------------------------------

@router.get("/")
async def get_requests(
    current_user: dict = Depends(get_current_user)
):
    department_id = current_user["department_id"]

    requests = await db.service_requests.find(
        {"department_id": department_id}
    ).to_list(length=None)

    result = []

    for request in requests:
        result.append({
            "request_id": str(request["_id"]),
            "request_no": request["request_no"],
            "title": request["title"],
            "description": request["description"],
            "category": request["category"],
            "priority": request["priority"],
            "status": request["status"],
            "created_at": request["created_at"],
            "updated_at": request["updated_at"]
        })

    return result


# ---------------------------------------------------------
# GET SINGLE REQUEST
# ---------------------------------------------------------

@router.get("/{request_id}")
async def get_request(
    request_id: str,
    current_user: dict = Depends(get_current_user)
):
    department_id = current_user["department_id"]

    request = await db.service_requests.find_one(
        {
            "_id": ObjectId(request_id),
            "department_id": department_id
        }
    )

    if not request:
        raise HTTPException(
            status_code=404,
            detail="Request not found"
        )

    return {
        "request_id": str(request["_id"]),
        "request_no": request["request_no"],
        "title": request["title"],
        "description": request["description"],
        "category": request["category"],
        "priority": request["priority"],
        "status": request["status"],
        "department_id": request["department_id"],
        "created_by": request["created_by"],
        "assigned_to": request["assigned_to"],
        "created_at": request["created_at"],
        "updated_at": request["updated_at"],
        "resolved_at": request["resolved_at"],
        "closed_at": request["closed_at"]
    }


# ---------------------------------------------------------
# ADD COMMENT
# ---------------------------------------------------------

@router.post("/{request_id}/comments")
async def add_comment(
    request_id: str,
    data: CreateComment,
    current_user: dict = Depends(get_current_user)
):
    department_id = current_user["department_id"]

    request = await db.service_requests.find_one(
        {
            "_id": ObjectId(request_id),
            "department_id": department_id
        }
    )

    if not request:
        raise HTTPException(
            status_code=404,
            detail="Request not found"
        )

    comment = {
        "request_id": ObjectId(request_id),
        "user_id": ObjectId(current_user["sub"]),
        "message": data.message,
        "created_at": datetime.now(timezone.utc)
    }

    result = await db.comments.insert_one(comment)

    return {
        "message": "Comment added successfully",
        "comment_id": str(result.inserted_id)
    }


# ---------------------------------------------------------
# GET COMMENTS
# ---------------------------------------------------------

@router.get("/{request_id}/comments")
async def get_comments(
    request_id: str,
    current_user: dict = Depends(get_current_user)
):
    department_id = current_user["department_id"]

    request = await db.service_requests.find_one(
        {
            "_id": ObjectId(request_id),
            "department_id": department_id
        }
    )

    if not request:
        raise HTTPException(
            status_code=404,
            detail="Request not found"
        )

    comments = await db.comments.find(
        {"request_id": ObjectId(request_id)}
    ).sort("created_at", 1).to_list(length=None)

    result = []

    for comment in comments:
        result.append({
            "comment_id": str(comment["_id"]),
            "user_id": str(comment["user_id"]),
            "message": comment["message"],
            "created_at": comment["created_at"]
        })

    return result


# ---------------------------------------------------------
# UPLOAD ATTACHMENT
# ---------------------------------------------------------

@router.post("/{request_id}/attachments")
async def upload_attachment(
    request_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    department_id = current_user["department_id"]

    request = await db.service_requests.find_one(
        {
            "_id": ObjectId(request_id),
            "department_id": department_id
        }
    )

    if not request:
        raise HTTPException(
            status_code=404,
            detail="Request not found"
        )

    upload_folder = Path("uploads")
    upload_folder.mkdir(exist_ok=True)

    file_path = upload_folder / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    attachment = {
        "request_id": ObjectId(request_id),
        "uploaded_by": ObjectId(current_user["sub"]),
        "file_name": file.filename,
        "file_path": str(file_path),
        "content_type": file.content_type,
        "created_at": datetime.now(timezone.utc)
    }

    result = await db.attachments.insert_one(attachment)

    return {
        "message": "Attachment uploaded successfully",
        "attachment_id": str(result.inserted_id),
        "file_name": file.filename
    }

# ---------------------------------------------------------
# CONFIRM RESOLUTION
# ---------------------------------------------------------

@router.post("/{request_id}/confirm-resolution")
async def confirm_resolution(
    request_id: str,
    current_user: dict = Depends(get_current_user)
):
    department_id = current_user["department_id"]

    request = await db.service_requests.find_one(
        {
            "_id": ObjectId(request_id),
            "department_id": department_id
        }
    )

    if not request:
        raise HTTPException(
            status_code=404,
            detail="Request not found"
        )

    if request["status"] != "RESOLVED":
        raise HTTPException(
            status_code=400,
            detail="Request is not ready to be closed"
        )

    now = datetime.now(timezone.utc)

    await db.service_requests.update_one(
        {
            "_id": ObjectId(request_id)
        },
        {
            "$set": {
                "status": "CLOSED",
                "closed_at": now,
                "updated_at": now
            }
        }
    )

    return {
        "message": "Resolution confirmed successfully",
        "request_id": request_id,
        "status": "CLOSED"
    }
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from models.user import GoogleUser, ProfileUpdate
import os
from database import db

router = APIRouter()

users_collection = db["users"]


@router.post("/google-login")
async def google_login(user: GoogleUser):
    user_in_db = await users_collection.find_one({"email": user.email})

    if user_in_db:
        return {"isNewUser": False}

    # First-time user — save basic Google data
    new_user = {
        "google_id": user.sub,
        "name": user.name,
        "email": user.email,
        "picture": user.picture,
    }

    await users_collection.insert_one(new_user)
    return {"isNewUser": True}

@router.post("/complete-profile")
async def complete_profile(data: ProfileUpdate):
    result = await users_collection.update_one(
        {"email": data.email},
        {"$set": {"mobile": data.mobile, "profession": data.profession}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"status": "Profile updated"}

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from models.user import GoogleUser, ProfileUpdate
import os
from database import db
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Fallback in-memory storage for testing when MongoDB is not available
in_memory_users = {}
use_fallback = False

try:
    users_collection = db["users"]
except Exception as e:
    logger.warning(f"MongoDB not available, using in-memory storage: {e}")
    use_fallback = True


@router.post("/google-login")
async def google_login(user: GoogleUser):
    try:
        logger.info(f"Google login attempt for email: {user.email}")
        
        if use_fallback:
            # Use in-memory storage
            user_in_db = in_memory_users.get(user.email)
            
            if user_in_db:
                logger.info(f"Existing user found (in-memory): {user.email}")
                return {"isNewUser": False, "user": user_in_db}

            # First-time user — save basic Google data
            new_user = {
                "google_id": user.sub,
                "name": user.name,
                "email": user.email,
                "picture": user.picture,
                "profile_completed": False,
                "created_at": None
            }

            in_memory_users[user.email] = new_user
            logger.info(f"New user created (in-memory): {user.email}")
            
            return {"isNewUser": True, "user": new_user}
        else:
            # Use MongoDB
            user_in_db = await users_collection.find_one({"email": user.email})
            
            if user_in_db:
                logger.info(f"Existing user found: {user.email}")
                # Convert ObjectId to string for JSON serialization
                if "_id" in user_in_db:
                    user_in_db["_id"] = str(user_in_db["_id"])
                return {"isNewUser": False, "user": user_in_db}

            # First-time user — save basic Google data
            new_user = {
                "google_id": user.sub,
                "name": user.name,
                "email": user.email,
                "picture": user.picture,
                "profile_completed": False,
                "created_at": None
            }

            result = await users_collection.insert_one(new_user)
            new_user["_id"] = str(result.inserted_id)
            logger.info(f"New user created: {user.email}, ID: {result.inserted_id}")
            
            return {"isNewUser": True, "user": new_user}
        
    except Exception as e:
        logger.error(f"Error in google_login: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


@router.post("/complete-profile")
async def complete_profile(data: ProfileUpdate):
    try:
        logger.info(f"Profile completion attempt for email: {data.email}")
        
        # Update user profile with additional information
        update_data = {
            "mobile": data.mobile,
            "profession": data.profession,
            "profile_completed": True,
            "updated_at": None
        }
        
        # Add any additional fields from the frontend
        if data.fullName:
            update_data["name"] = data.fullName
        if data.location:
            update_data["location"] = data.location
        if data.interests:
            update_data["interests"] = data.interests
        
        if use_fallback:
            # Use in-memory storage
            if data.email not in in_memory_users:
                logger.error(f"User not found for profile completion (in-memory): {data.email}")
                raise HTTPException(status_code=404, detail="User not found")
            
            # Update user data
            in_memory_users[data.email].update(update_data)
            updated_user = in_memory_users[data.email]
            logger.info(f"Profile completed successfully (in-memory) for: {data.email}")
            
        else:
            # Use MongoDB
            result = await users_collection.update_one(
                {"email": data.email},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                logger.error(f"User not found for profile completion: {data.email}")
                raise HTTPException(status_code=404, detail="User not found")
            
            # Get updated user data
            updated_user = await users_collection.find_one({"email": data.email})
            if "_id" in updated_user:
                updated_user["_id"] = str(updated_user["_id"])
            logger.info(f"Profile completed successfully for: {data.email}")
        
        return {
            "status": "Profile updated successfully",
            "user": updated_user
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in complete_profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Profile completion failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for authentication service"""
    try:
        # Test database connection
        await users_collection.find_one({}, {"_id": 1})
        return {"status": "healthy", "service": "authentication"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable")

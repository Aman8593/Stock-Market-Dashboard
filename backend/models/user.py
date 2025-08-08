from pydantic import BaseModel, EmailStr
from typing import Optional

class GoogleUser(BaseModel):
    sub: str  # Google ID
    name: str
    email: EmailStr
    picture: Optional[str] = None

class ProfileUpdate(BaseModel):
    email: EmailStr
    mobile: Optional[str] = None
    profession: Optional[str] = None

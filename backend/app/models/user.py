"""
User Model
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

class User(BaseModel):
    """User model"""
    _id: Optional[str] = None
    email: EmailStr
    username: str
    password_hash: str
    full_name: str
    is_active: bool = True
    is_superuser: bool = False
    roles: List[str] = ["user"]
    permissions: List[str] = []
    company: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    last_login: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserCreate(BaseModel):
    """User creation model"""
    email: EmailStr
    username: str
    password: str
    full_name: str
    company: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None

class UserUpdate(BaseModel):
    """User update model"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    company: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    roles: Optional[List[str]] = None

class UserInDB(User):
    """User as stored in database"""
    password_hash: str

"""
Authentication Schemas
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.models.user import User

class Token(BaseModel):
    """Token response"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Token data"""
    user_id: str
    email: str
    username: str
    roles: List[str] = []
    permissions: List[str] = []

class LoginRequest(BaseModel):
    """Login request"""
    username: str
    password: str

class UserResponse(BaseModel):
    """User response with token"""
    user: User
    access_token: str
    token_type: str

class ChangePasswordRequest(BaseModel):
    """Change password request"""
    current_password: str
    new_password: str

class ResetPasswordRequest(BaseModel):
    """Reset password request"""
    email: EmailStr

class ResetPasswordConfirm(BaseModel):
    """Reset password confirm"""
    token: str
    new_password: str

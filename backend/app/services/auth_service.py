"""
Authentication Service
"""

from datetime import datetime
from typing import Optional, Tuple
from app.core.database import Database
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User, UserCreate, UserInDB
from app.schemas.auth import TokenData
import uuid

class AuthService:
    """Authentication service"""
    
    def __init__(self):
        self.db = Database()
        self.collection = "users"
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user"""
        # Find user by username or email
        user_data = self.db.find_one(
            self.collection,
            {"$or": [{"username": username}, {"email": username}]}
        )
        
        if not user_data:
            return None
        
        # Verify password
        if not verify_password(password, user_data.get("password_hash", "")):
            return None
        
        # Update last login
        self.db.update(
            self.collection,
            {"_id": user_data["_id"]},
            {"last_login": datetime.utcnow().isoformat()}
        )
        
        return User(**user_data)
    
    async def create_user(self, user_data: UserCreate) -> Tuple[User, str]:
        """Create new user"""
        # Check if user exists
        existing = self.db.find_one(
            self.collection,
            {"$or": [{"email": user_data.email}, {"username": user_data.username}]}
        )
        
        if existing:
            raise ValueError("User with this email or username already exists")
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user
        user_dict = user_data.dict()
        user_dict["_id"] = str(uuid.uuid4())
        user_dict["password_hash"] = hashed_password
        user_dict["created_at"] = datetime.utcnow().isoformat()
        user_dict["updated_at"] = datetime.utcnow().isoformat()
        
        # Remove password from dict
        del user_dict["password"]
        
        # Save to database
        self.db.insert(self.collection, user_dict)
        
        # Create access token
        token = create_access_token(
            data={"sub": user_dict["_id"], "email": user_dict["email"]}
        )
        
        return User(**user_dict), token
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        user_data = self.db.find_one(self.collection, {"_id": user_id})
        if user_data:
            return User(**user_data)
        return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        user_data = self.db.find_one(self.collection, {"email": email})
        if user_data:
            return User(**user_data)
        return None
    
    async def update_user(self, user_id: str, update_data: dict) -> Optional[User]:
        """Update user"""
        update_data["updated_at"] = datetime.utcnow().isoformat()
        count = self.db.update(self.collection, {"_id": user_id}, update_data)
        
        if count > 0:
            return await self.get_user_by_id(user_id)
        return None
    
    async def get_token_data(self, token: str) -> Optional[TokenData]:
        """Get token data from JWT"""
        from app.core.security import decode_token
        payload = decode_token(token)
        if not payload:
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        return TokenData(
            user_id=user_id,
            email=user.email,
            username=user.username,
            roles=user.roles,
            permissions=user.permissions
        )

"""
FastAPI Dependencies
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from app.services.auth_service import AuthService
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
auth_service = AuthService()

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current user from token"""
    token_data = await auth_service.get_token_data(token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await auth_service.get_user_by_id(token_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

async def get_current_superuser(current_user: User = Depends(get_current_active_user)) -> User:
    """Get current superuser"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

def require_permission(permission: str):
    """Dependency to check permission"""
    async def check_permission(current_user: User = Depends(get_current_active_user)):
        if permission not in current_user.permissions and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission: {permission}"
            )
        return current_user
    return check_permission

def require_role(role: str):
    """Dependency to check role"""
    async def check_role(current_user: User = Depends(get_current_active_user)):
        if role not in current_user.roles and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing role: {role}"
            )
        return current_user
    return check_role

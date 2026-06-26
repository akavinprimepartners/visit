"""
Authentication Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Any
from app.schemas.auth import Token, UserResponse, LoginRequest
from app.schemas.user import UserCreate, UserUpdate
from app.services.auth_service import AuthService
from app.core.dependencies import get_current_user, get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])
auth_service = AuthService()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate) -> Any:
    """Register new user"""
    try:
        user, token = await auth_service.create_user(user_data)
        return UserResponse(
            user=user,
            access_token=token,
            token_type="bearer"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=UserResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """Login user"""
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    token = create_access_token(
        data={"sub": user._id, "email": user.email}
    )
    
    return UserResponse(
        user=user,
        access_token=token,
        token_type="bearer"
    )

@router.post("/login/json", response_model=UserResponse)
async def login_json(login_data: LoginRequest) -> Any:
    """Login user with JSON body"""
    user = await auth_service.authenticate_user(login_data.username, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    token = create_access_token(
        data={"sub": user._id, "email": user.email}
    )
    
    return UserResponse(
        user=user,
        access_token=token,
        token_type="bearer"
    )

@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)) -> Any:
    """Get current user info"""
    return current_user

@router.put("/me", response_model=User)
async def update_current_user(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Update current user"""
    updated_user = await auth_service.update_user(
        current_user._id,
        update_data.dict(exclude_unset=True)
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return updated_user

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)) -> Any:
    """Logout user (client-side token discard)"""
    return {"message": "Successfully logged out"}

# Import create_access_token from security
from app.core.security import create_access_token

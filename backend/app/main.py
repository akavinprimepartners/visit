"""
AKAVIN OS - FastAPI Backend
Phase 1: Core Framework
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
from typing import Dict, Any

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import AppException
from app.core.database import Database
from app.api.v1.endpoints import auth, cards, users

# Setup logging
logger = setup_logging()

# Create FastAPI app
app = FastAPI(
    title="AKAVIN OS API",
    version="1.0.0",
    description="AI-Powered Business Operating System",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db = Database()

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("🚀 AKAVIN OS API starting...")
    await db.connect()
    logger.info("✅ Database connected")
    logger.info(f"📁 Data directory: {settings.DATA_DIR}")
    logger.info(f"🔧 Environment: {settings.ENV}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await db.disconnect()
    logger.info("👋 AKAVIN OS API shutting down...")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "AKAVIN OS API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": "connected",
            "redis": "connected",
            "elasticsearch": "connected"
        }
    }

@app.get("/api/v1/system/info")
async def system_info():
    """System information"""
    return {
        "system": "AKAVIN OS",
        "version": "1.0.0",
        "environment": settings.ENV,
        "modules": [
            "core",
            "storage",
            "auth",
            "ocr",
            "ai",
            "search"
        ],
        "features": [
            "contact_management",
            "company_management",
            "product_catalog",
            "search",
            "analytics"
        ]
    }

# Add user endpoint
@router.get("/api/v1/users", response_model=List[User])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_superuser)
):
    """Get all users (admin only)"""
    users_data = db.find("users", {})
    return users_data[skip:skip + limit]

# Import routers
# from app.api.v1.endpoints import cards, contacts, companies, products, search

# app.include_router(cards.router, prefix="/api/v1/cards", tags=["Cards"])
# app.include_router(contacts.router, prefix="/api/v1/contacts", tags=["Contacts"])
# app.include_router(companies.router, prefix="/api/v1/companies", tags=["Companies"])
# app.include_router(products.router, prefix="/api/v1/products", tags=["Products"])
# app.include_router(search.router, prefix="/api/v1/search", tags=["Search"])

# Add routers
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(cards.router, prefix="/api/v1", tags=["Business Cards"])
app.include_router(users.router, prefix="/api/v1", tags=["Users"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

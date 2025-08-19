import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables
load_dotenv()

# Import our config and routes
from config.firebase_config import init_firebase
from config.database import init_db
from routes.auth import router as auth_router
from routes.videos import router as videos_router
from routes.users import router as users_router
from routes.likes import router as likes_router
from routes.ml import router as ml_router

# Import models to ensure they're registered
from models.models import User, Video, Like, AnalyticsData

# Initialize Firebase
init_firebase()

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="Comedy Peach Backend",
    description="Backend for Comedy Platform with Firebase authentication, video uploads, and AI analytics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "authentication", "description": "Firebase authentication operations"},
        {"name": "users", "description": "User profile and management operations"},
        {"name": "videos", "description": "Video upload and management operations"},
        {"name": "likes", "description": "Video like/unlike operations"},
        {"name": "ml_processing", "description": "ML analytics and processing operations"}
    ]
)

# Add security scheme for Swagger UI
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Firebase JWT token. Get this from the test-auth-ui page after signing in."
        }
    }
    
    # Add security to specific paths that need it
    protected_paths = [
        "/api/users/me",
        "/api/users/me/settings", 
        "/api/users/{user_id}",
        "/api/users/{user_id}/videos",
        "/api/videos/",
        "/api/videos/{video_id}",
        "/api/videos/{video_id}/analytics",
        "/api/videos/{video_id}/like",
        "/api/ml/analyze"
    ]
    
    for path in openapi_schema["paths"]:
        if any(path.startswith(protected) or path.replace("{user_id}", "123").replace("{video_id}", "123") in protected_paths for protected in protected_paths):
            for method in openapi_schema["paths"][path]:
                if method.lower() in ["get", "post", "put", "delete"]:
                    openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all route modules
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(videos_router, prefix="/api/videos", tags=["videos"])
app.include_router(users_router, prefix="/api/users", tags=["users"])
app.include_router(likes_router, prefix="/api/videos", tags=["likes"])  # Nested under videos
app.include_router(ml_router, prefix="/api/ml", tags=["ml_processing"])

# Mount static files for test UI
test_ui_path = Path(__file__).parent / "test-auth-ui"
if test_ui_path.exists():
    app.mount("/test-auth-ui", StaticFiles(directory=test_ui_path, html=True), name="test-auth-ui")

# Mount upload test UI
upload_test_ui_path = Path(__file__).parent / "test-upload-ui"
if upload_test_ui_path.exists():
    app.mount("/test-upload-ui", StaticFiles(directory=upload_test_ui_path, html=True), name="test-upload-ui")

# Add a test endpoint to help debug authentication
@app.get("/test-auth")
async def test_auth():
    """Test endpoint to verify authentication is working"""
    return {
        "message": "Authentication test endpoint",
        "instructions": [
            "1. Go to http://localhost:8000/test-auth-ui",
            "2. Sign in with Firebase",
            "3. Copy your bearer token",
            "4. Use the token in Swagger UI or test with curl:",
            "   curl -H 'Authorization: Bearer YOUR_TOKEN' http://localhost:8000/api/users/me"
        ]
    }

# Health check endpoint
@app.get("/")
async def health_check():
    return {
        "message": "Comedy Peach Backend is running!",
        "framework": "FastAPI",
        "version": "1.0.0",
        "storage_backend": os.getenv("STORAGE_BACKEND", "local"),
        "database": "SQLite" if os.getenv("DATABASE_URL", "").startswith("sqlite") else "PostgreSQL",
        "endpoints": {
            "health": "/",
            "auth": "/api/auth",
            "videos": "/api/videos", 
            "users": "/api/users",
            "ml": "/api/ml",
            "testUI": "/test-auth-ui",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "features": [
            "Firebase Authentication",
            "Video/Audio Upload & Storage",
            "User Profile Management", 
            "Like System",
            "Feed with Pagination",
            "ML Analytics Integration",
            "Transcript Management"
        ]
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    print(f"Global exception handler caught: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc)
        }
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    storage_backend = os.getenv("STORAGE_BACKEND", "local")
    
    print("🍑 Comedy Peach Backend Starting...")
    print(f"🚀 Server: http://localhost:{port}")
    print(f"🔧 Test UI: http://localhost:{port}/test-auth-ui")
    print(f"📚 API Docs: http://localhost:{port}/docs")
    print(f"💾 Database: {'SQLite' if os.getenv('DATABASE_URL', '').startswith('sqlite') else 'PostgreSQL'}")
    print(f"📦 Storage: {storage_backend.upper()}")
    print("\n✨ Features:")
    print("   • Firebase Authentication")
    print("   • Video/Audio Upload & Streaming") 
    print("   • User Profile Management")
    print("   • Like & Feed System")
    print("   • ML Analytics Integration")
    print("   • Transcript & Playback Management")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    ) 
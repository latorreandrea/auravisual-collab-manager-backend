from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Load dotenv only in development (not available in Cloud Run)
if os.getenv("ENVIRONMENT") == "development":
    from dotenv import load_dotenv
    load_dotenv()

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = ENVIRONMENT == "development"

# Initialize FastAPI app with environment-specific settings
app = FastAPI(
    title="Auravisual Collab",
    version="1.0.0"
)

# CORS origins configuration
if DEBUG:
    # Development: allow all origins
    CORS_ORIGINS = ["*"]  
else:
    # Production: get allowed origins from Cloud Run environment variables
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "")
    CORS_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS.split(",") if origin.strip()]

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"] if DEBUG else ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Health check endpoint (required for Cloud Run)
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "auravisual-backend"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Auravisual Collab Manager API", 
        "version": app.version,
        "status": "running"
    }

# Server startup configuration
if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment (Cloud Run sets PORT automatically)
    port = int(os.getenv("PORT", 8000))
    
    if DEBUG:
        # Development: reload enabled, debug logs
        uvicorn.run(
            "main:app", 
            host="0.0.0.0", 
            port=port, 
            reload=True,
            log_level="debug"
        )
    else:
        # Production: optimized for Cloud Run
        uvicorn.run(
            "main:app", 
            host="0.0.0.0", 
            port=port, 
            reload=False,
            log_level="info"
        )
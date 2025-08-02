from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings, get_app_config, get_cors_config, get_server_config

# Initialize FastAPI app with centralized configuration
app = FastAPI(**get_app_config())

# Add CORS middleware
app.add_middleware(CORSMiddleware, **get_cors_config())

@app.get("/")
async def root():
    return {
        "message": "Auravisual Collab Manager API", 
        "version": settings.project_version,
        "status": "running",
        "environment": settings.environment
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "auravisual-backend"}

# Debug endpoint (only in development)
if settings.debug:
    @app.get("/debug/config")
    async def debug_config():
        return {
            "environment": settings.environment,
            "debug": settings.debug,
            "cors_origins": settings.cors_origins,
            "api_docs_enabled": bool(settings.docs_url)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", **get_server_config())
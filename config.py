import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """
    Application settings configuration
    This class loads configuration from environment variables
    and provides default values.
    """
    
    # Environment configuration
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = environment == "development"
    
    # Supabase configuration
    supabase_url: str = os.getenv("SUPABASE_URL")
    supabase_key: str = os.getenv("SUPABASE_KEY")
    supabase_service_key: str = os.getenv("SUPABASE_SERVICE_KEY")
    
    # JWT configuration
    secret_key: str = os.getenv("SECRET_KEY")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # API configuration
    project_name: str = "Auravisual Collab Manager API"
    project_description: str = "Backend API for project management and collaboration"
    project_version: str = "1.0.0"
    
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    @property
    def docs_url(self):
        """Enable API docs only in development"""
        return "/docs" if self.debug else None
    
    @property
    def redoc_url(self):
        """Enable ReDoc only in development"""
        return "/redoc" if self.debug else None
    
    @property
    def openapi_url(self):
        """Enable OpenAPI JSON only in development"""
        return "/openapi.json" if self.debug else None
    
    @property
    def cors_origins(self):
        """Get CORS origins based on environment"""
        if self.debug:
            # Even in dev, be more restrictive
            return [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:8080",  # Flutter web dev
                "http://127.0.0.1:8080"
            ]
        
        # In production, get from environment variable
        allowed_origins = os.getenv("ALLOWED_ORIGINS", "")
        if allowed_origins:
                origins = [origin.strip() for origin in allowed_origins.split(",") if origin.strip()]
            # Add your main domain and subdomains
            origins.extend([
                "https://www.auravisual.dk",
                "https://app.auravisual.dk", 
                "https://client.auravisual.dk"
            ])
            return list(set(origins))

settings = Settings()

# Helper functions for configuration
def get_app_config() -> dict:
    """Get FastAPI application configuration"""
    return {
        "title": settings.project_name,
        "description": settings.project_description,
        "version": settings.project_version,
        "docs_url": settings.docs_url,
        "redoc_url": settings.redoc_url,
        "openapi_url": settings.openapi_url
    }

def get_cors_config() -> dict:
    """Get CORS middleware configuration"""
    return {
        "allow_origins": settings.cors_origins,
        "allow_credentials": True,
        "allow_methods": ["*"] if settings.debug else ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["*"]
    }

def get_server_config() -> dict:
    """Get Uvicorn server configuration"""
    return {
        "host": settings.host,
        "port": int(os.getenv("PORT", settings.port)),  # Cloud Run sets PORT
        "reload": settings.debug,
        "log_level": "debug" if settings.debug else "info"
    }

def get_supabase_config() -> dict:
    """Get Supabase client configuration"""
    return {
        "url": settings.supabase_url,
        "key": settings.supabase_key
    }

def get_supabase_admin_config() -> dict:
    """Get Supabase admin configuration"""
    return {
        "url": settings.supabase_url,
        "key": settings.supabase_service_key
    }

def get_jwt_config() -> dict:
    """Get JWT configuration"""
    return {
        "secret_key": settings.secret_key,
        "algorithm": settings.algorithm,
        "expire_minutes": settings.access_token_expire_minutes
    }

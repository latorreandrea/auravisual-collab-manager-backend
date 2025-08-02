from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config import settings, get_app_config, get_cors_config, get_server_config
from database import test_connection, get_db, get_all_users, get_users_by_role, Client
from utils.auth import get_current_user, require_admin, require_admin_or_staff
from typing import Dict

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

# Public database health check (limited info)
@app.get("/health/db")
async def database_health():
    """Test database connectivity (public endpoint)"""
    result = await test_connection()
    # Return only basic status, hide sensitive info
    return {
        "status": result.get("status"),
        "database": "connected" if result.get("status") == "connected" else "error"
    }

# Protected user management endpoints
@app.get("/admin/users")
async def list_all_users(current_user: Dict = Depends(require_admin)):
    """List all users (admin only)"""
    users = await get_all_users()
    return {
        "total_users": len(users),
        "users": users,
        "requested_by": current_user.get("username")
    }

@app.get("/admin/users/clients")
async def list_clients(current_user: Dict = Depends(require_admin_or_staff)):
    """List all clients (admin/staff only)"""
    clients = await get_users_by_role("client")
    return {
        "total_clients": len(clients),
        "clients": clients,
        "requested_by": current_user.get("username")
    }

@app.get("/admin/users/staff")
async def list_internal_staff(current_user: Dict = Depends(require_admin)):
    """List all internal staff (admin only)"""
    staff = await get_users_by_role("internal_staff")
    return {
        "total_staff": len(staff),
        "staff": staff,
        "requested_by": current_user.get("username")
    }

# User profile endpoints
@app.get("/profile/me")
async def get_my_profile(current_user: Dict = Depends(get_current_user)):
    """Get current user profile"""
    # Remove sensitive fields
    safe_user = {k: v for k, v in current_user.items() if k not in ['created_at', 'updated_at']}
    return safe_user

# Debug endpoints (only in development and with admin access)
if settings.debug:
    @app.get("/debug/config")
    async def debug_config(current_user: Dict = Depends(require_admin)):
        """Debug configuration (admin only, dev only)"""
        return {
            "environment": settings.environment,
            "debug": settings.debug,
            "cors_origins": settings.cors_origins,
            "api_docs_enabled": bool(settings.docs_url),
            "supabase_configured": bool(settings.supabase_key),
            "accessed_by": current_user.get("username")
        }
    
    @app.get("/debug/db")
    async def debug_database(
        current_user: Dict = Depends(require_admin),
        db: Client = Depends(get_db)
    ):
        """Debug database connection (admin only, dev only)"""
        try:
            response = db.from_("users").select("*").limit(1).execute()
            return {
                "status": "success",
                "connection": "established",
                "table": "users",
                "response_received": bool(response.data is not None),
                "data_count": len(response.data) if response.data else 0,
                "accessed_by": current_user.get("username")
            }
        except Exception as e:
            return {
                "status": "error",
                "connection": "failed",
                "error": str(e),
                "accessed_by": current_user.get("username")
            }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", **get_server_config())
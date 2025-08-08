from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from config import settings, get_app_config, get_cors_config, get_server_config
from database import test_connection, get_db, get_all_users, get_users_by_role, Client, get_supabase_client, get_supabase_admin_client, get_user_by_id
from supabase import create_client
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

@app.post("/auth/register")
async def register(user_data: dict, current_user: Dict = Depends(require_admin)):
    """Register new user (admin only)"""
    try:
        email = user_data.get("email")
        password = user_data.get("password")
        full_name = user_data.get("full_name")
        role = user_data.get("role", "client")
        
        if not all([email, password, full_name]):
            raise HTTPException(
                status_code=400,
                detail="Email, password and full_name required"
            )
        
        # Role validation
        allowed_roles = ["admin", "internal_staff", "client"]
        if role not in allowed_roles:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid role. Must be one of: {allowed_roles}"
            )
        
        # Create auth user - USE ADMIN CLIENT (service key)
        admin_client = get_supabase_admin_client()
        auth_response = admin_client.auth.sign_up({
            "email": email,
            "password": password
        })
        
        if auth_response.user:
            # Create user profile
            profile_data = {
                "id": auth_response.user.id,
                "email": email,
                "username": email.split("@")[0],
                "full_name": full_name,
                "role": role,
                "is_active": True,
                "email_verified": False
            }
            
            # Insert profile - ALREADY USING ADMIN CLIENT
            admin_client.from_("users").insert(profile_data).execute()
            
            return {
                "message": "User registered successfully",
                "user_id": auth_response.user.id,
                "email": email,
                "role": role,
                "created_by": current_user.get("username")
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Registration failed"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Registration failed: {str(e)}"
        )

# User profile endpoints

# User authentication endpoints

@app.post("/auth/login")
async def login(credentials: dict):
    """Login with email/password"""
    try:
        email = credentials.get("email")
        password = credentials.get("password") 
        
        if not email or not password:
            raise HTTPException(
                status_code=400, 
                detail="Email and password required"
            )
        
        # Use Supabase Auth to sign in
        client = get_supabase_client()
        response = client.auth.sign_in_with_password({
            "email": email, 
            "password": password
        })
        
        if response.user and response.session:
            # Get user profile - USE ADMIN CLIENT to bypass RLS
            admin_client = get_supabase_admin_client()
            profile_response = admin_client.from_("users").select("*").eq("id", response.user.id).single().execute()
            user_profile = profile_response.data if profile_response.data else None
            
            return {
                "access_token": response.session.access_token,
                "token_type": "bearer",
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                    "username": user_profile.get("username") if user_profile else None,
                    "role": user_profile.get("role") if user_profile else "client",
                    "full_name": user_profile.get("full_name") if user_profile else None
                }
            }
        else:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Login failed: {str(e)}"
        )

@app.post("/auth/logout")
async def logout(current_user: Dict = Depends(get_current_user)):
    """Logout user"""
    try:
        client = get_supabase_client()
        client.auth.sign_out()
        return {"message": "Logged out successfully"}
    except Exception as e:
        return {"message": "Logout completed", "note": str(e)}

@app.get("/auth/me")
async def get_current_user_info(current_user: Dict = Depends(get_current_user)):
    """Get current authenticated user info"""
    return {
        "user": current_user,
        "authenticated": True
    }
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
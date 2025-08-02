from supabase import create_client, Client
from config import settings, get_supabase_config, get_supabase_admin_config
from typing import Optional, Dict, List
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Global Supabase clients
supabase_client: Optional[Client] = None
supabase_admin_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """
    Get the regular Supabase client (with anon key)
    Used for standard operations with RLS policies
    """
    global supabase_client
    
    if supabase_client is None:
        config = get_supabase_config()
        supabase_client = create_client(config["url"], config["key"])
        logger.info("Supabase client initialized")
    
    return supabase_client

def get_supabase_admin_client() -> Client:
    """
    Get the admin Supabase client (with service role key)
    Used for admin operations that bypass RLS policies
    """
    global supabase_admin_client
    
    if supabase_admin_client is None:
        config = get_supabase_admin_config()
        supabase_admin_client = create_client(config["url"], config["key"])
        logger.info("Supabase admin client initialized")
    
    return supabase_admin_client

async def test_connection() -> dict:
    """Test the database connection"""
    try:
        client = get_supabase_client()
        
        # Test connection with a simple query to users table
        response = client.from_("users").select("count", count="exact").execute()
        
        return {
            "status": "connected",
            "database": "supabase",
            "table": "users",
            "tables_accessible": True,
            "environment": settings.environment,
            "users_count": response.count if hasattr(response, 'count') else 0
        }
    
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return {
            "status": "error",
            "database": "supabase", 
            "error": str(e),
            "environment": settings.environment
        }

# User management functions
async def get_all_users() -> List[Dict]:
    """Get all users (admin only)"""
    try:
        admin_client = get_supabase_admin_client()
        response = admin_client.from_("users").select("*").execute()
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        return []

async def get_user_by_id(user_id: str) -> Optional[Dict]:
    """Get user by ID"""
    try:
        client = get_supabase_client()
        response = client.from_("users").select("*").eq("id", user_id).single().execute()
        return response.data if response.data else None
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {str(e)}")
        return None

async def get_users_by_role(role: str) -> List[Dict]:
    """Get users by role (admin, internal_staff, client)"""
    try:
        admin_client = get_supabase_admin_client()
        response = admin_client.from_("users").select("*").eq("role", role).execute()
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Error fetching users with role {role}: {str(e)}")
        return []
        
# Database dependencies for FastAPI
def get_db() -> Client:
    """Dependency to inject database client into FastAPI endpoints"""
    return get_supabase_client()

def get_admin_db() -> Client:
    """Dependency to inject admin database client into FastAPI endpoints"""
    return get_supabase_admin_client()
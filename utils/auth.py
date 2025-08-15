from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict
from database import get_supabase_client, get_supabase_admin_client, get_user_by_id
import logging

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """Get current authenticated user from Supabase token"""
    try:
        token = credentials.credentials
        logger.info(f"🔍 DEBUG: Received token: {token[:50]}...")
        
        # Use Supabase to verify the token
        client = get_supabase_client()
        
        logger.info("🔍 DEBUG: Using Supabase client to verify token")
        
        # Verify token with Supabase
        response = client.auth.get_user(token)
        
        logger.info(f"🔍 DEBUG: Supabase response: {response.user is not None}")
        
        if response.user:
            # Get user profile from database using admin client
            admin_client = get_supabase_admin_client()
            profile_response = admin_client.from_("users").select("*").eq("id", response.user.id).single().execute()
            
            if profile_response.data:
                user_profile = profile_response.data
                logger.info(f"🔍 DEBUG: User profile found: {user_profile.get('email')}")
                
                # Check if user is active
                if not user_profile.get("is_active", False):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="User account is disabled"
                    )
                
                return user_profile
            else:
                logger.error("🔍 DEBUG: User profile not found in database")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User profile not found"
                )
        else:
            logger.error("🔍 DEBUG: Supabase token validation failed")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"🔍 DEBUG: Token validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(e)}"
        )

async def require_admin(current_user: Dict = Depends(get_current_user)) -> Dict:
    """Require admin role for endpoint access"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user

async def require_admin_or_staff(current_user: Dict = Depends(get_current_user)) -> Dict:
    """Require admin or internal_staff role"""
    allowed_roles = ["admin", "internal_staff"]
    if current_user.get("role") not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or staff access required"
        )
    
    return current_user
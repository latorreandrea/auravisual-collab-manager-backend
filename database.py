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

async def get_user_task_counts(user_id: str) -> Dict:
    """Get task counts for a specific user with status breakdown"""
    try:
        admin_client = get_supabase_admin_client()
        
        # Count total tasks assigned to user
        total_response = admin_client.from_("tasks").select("id", count="exact").eq("assigned_to", user_id).execute()
        total_assigned = total_response.count or 0
        
        # Count active tasks (in_progress only)
        active_response = admin_client.from_("tasks").select("id", count="exact").eq("assigned_to", user_id).eq("status", "in_progress").execute()
        active_tasks = active_response.count or 0
        
        return {
            "total_assigned": total_assigned,
            "active_tasks": active_tasks
        }
        
    except Exception as e:
        logger.error(f"Error getting task counts for user {user_id}: {str(e)}")
        return {
            "total_assigned": 0,
            "active_tasks": 0
        }

async def get_tasks_by_user(user_id: str, status_filter: str = None) -> List[Dict]:
    """Get tasks assigned to a specific user with optional status filter"""
    try:
        admin_client = get_supabase_admin_client()
        
        query = admin_client.from_("tasks").select("""
            id,
            ticket_id,
            action,
            priority,
            status,
            created_at,
            updated_at,
            tickets:ticket_id (
                id,
                message,
                status,
                projects:project_id (
                    id,
                    name,
                    client_id,
                    users:client_id (
                        full_name,
                        email
                    )
                )
            )
        """).eq("assigned_to", user_id)
        
        if status_filter:
            query = query.eq("status", status_filter)
        
        response = query.order("created_at", desc=True).execute()
        return response.data if response.data else []
        
    except Exception as e:
        logger.error(f"Error getting tasks for user {user_id}: {str(e)}")
        return []


async def update_task_status(task_id: str, new_status: str, user_id: str) -> Dict:
    """Update task status (only by assigned user or admin)"""
    try:
        admin_client = get_supabase_admin_client()
        
        # First verify the task exists and user has permission
        task_check = admin_client.from_("tasks").select("assigned_to").eq("id", task_id).single().execute()
        
        if not task_check.data:
            return {"error": "Task not found"}
        
        # Check if user is assigned to this task or is admin
        user_role_check = admin_client.from_("users").select("role").eq("id", user_id).single().execute()
        user_role = user_role_check.data.get("role") if user_role_check.data else None
        
        if task_check.data["assigned_to"] != user_id and user_role != "admin":
            return {"error": "Permission denied"}
        
        # Update task status
        response = admin_client.from_("tasks").update({
            "status": new_status
        }).eq("id", task_id).execute()
        
        return response.data[0] if response.data else {"error": "Update failed"}
        
    except Exception as e:
        logger.error(f"Error updating task status: {str(e)}")
        return {"error": str(e)}


async def get_users_by_role_with_tasks(role: str) -> List[Dict]:
    """Get users by role with task counts"""
    try:
        admin_client = get_supabase_admin_client()
        
        # Get users by role
        response = admin_client.from_("users").select("*").eq("role", role).order("created_at").execute()
        users = response.data if response.data else []
        
        # Add task counts for each user
        for user in users:
            task_counts = await get_user_task_counts(user["id"])
            user["task_counts"] = task_counts
        
        return users
        
    except Exception as e:
        logger.error(f"Error fetching users with role {role}: {str(e)}")
        return []


async def create_task(ticket_id: str, assigned_to: str, action: str, priority: str = "medium") -> Dict:
    """Create a new task (admin only)"""
    try:
        admin_client = get_supabase_admin_client()
        
        # Validate that ticket exists
        ticket_check = admin_client.from_("tickets").select("id").eq("id", ticket_id).single().execute()
        if not ticket_check.data:
            return {"error": "Ticket not found"}
        
        # Validate that assigned user exists
        user_check = admin_client.from_("users").select("id").eq("id", assigned_to).single().execute()
        if not user_check.data:
            return {"error": "Assigned user not found"}
        
        task_data = {
            "ticket_id": ticket_id,
            "assigned_to": assigned_to,
            "action": action,
            "priority": priority,
            "status": "in_progress"  # Default status
        }
        
        response = admin_client.from_("tasks").insert(task_data).execute()
        return response.data[0] if response.data else {"error": "Failed to create task"}
        
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        return {"error": str(e)}


async def get_all_projects_with_relations() -> List[Dict]:
    """Return all projects with related client, tickets and tasks (admin client)."""
    try:
        admin_client = get_supabase_admin_client()
        # Nested select: clients from client_id, tickets by project_id, tasks by ticket_id
        response = admin_client.from_("projects").select("""
            id,
            name,
            description,
            client_id,
            website,
            socials,
            plan,
            contract_subscription_date,
            status,
            created_at,
            updated_at,
            clients:client_id ( id, email, username, full_name ),
            tickets:project_id (
                id,
                message,
                status,
                task_ids,
                created_at,
                updated_at,
                tasks:ticket_id (
                    id,
                    action,
                    assigned_to,
                    status,
                    priority,
                    created_at,
                    updated_at
                )
            )
        """).order("created_at", desc=True).execute()
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Error fetching projects with relations: {str(e)}")
        return []

async def get_project_with_relations(project_id: str) -> Optional[Dict]:
    """Return single project with related client, tickets and tasks (admin client)."""
    try:
        admin_client = get_supabase_admin_client()
        response = admin_client.from_("projects").select("""
            id,
            name,
            description,
            client_id,
            website,
            socials,
            plan,
            contract_subscription_date,
            status,
            created_at,
            updated_at,
            clients:client_id ( id, email, username, full_name ),
            tickets:project_id (
                id,
                message,
                status,
                task_ids,
                created_at,
                updated_at,
                tasks:ticket_id (
                    id,
                    action,
                    assigned_to,
                    status,
                    priority,
                    created_at,
                    updated_at
                )
            )
        """).eq("id", project_id).single().execute()
        return response.data if response.data else None
    except Exception as e:
        logger.error(f"Error fetching project {project_id}: {str(e)}")
        return None


async def create_tasks_bulk(ticket_id: str, tasks: List[Dict]) -> Dict:
    """Create multiple tasks for a ticket (admin only). Also set ticket status to 'processing'"""
    try:
        admin_client = get_supabase_admin_client()
        # Verify ticket exists
        ticket_check = admin_client.from_("tickets").select("id, client_id").eq("id", ticket_id).single().execute()
        if not ticket_check.data:
            return {"error": "Ticket not found"}

        # Validate users and prepare insert payload
        insert_payload = []
        valid_priorities = {"low", "medium", "high", "urgent"}
        for t in tasks:
            task = t.get("task") or t.get("task") or t.get("task_action")
            assigned_to = t.get("assigned_to")
            priority = t.get("priority", "medium")

            if not task or not assigned_to:
                return {"error": "Each task must include 'task' and 'assigned_to'"}
            if priority not in valid_priorities:
                return {"error": f"Invalid priority '{priority}'. Allowed: {list(valid_priorities)}"}

            # Validate assigned user exists
            user_check = admin_client.from_("users").select("id").eq("id", assigned_to).single().execute()
            if not user_check.data:
                return {"error": f"Assigned user not found: {assigned_to}"}

            insert_payload.append({
                "ticket_id": ticket_id,
                "assigned_to": assigned_to,
                "task": task,
                "priority": priority,
                "status": "in_progress"
            })

        if not insert_payload:
            return {"error": "No valid tasks to create"}

        # Insert tasks in bulk
        response = admin_client.from_("tasks").insert(insert_payload).execute()
        created = response.data if response.data else []

        # Update ticket status to processing
        admin_client.from_("tickets").update({"status": "processing"}).eq("id", ticket_id).execute()

        return {"tasks": created, "ticket_id": ticket_id, "ticket_status": "processing"}

    except Exception as e:
        logger.error(f"Error creating tasks bulk for ticket {ticket_id}: {str(e)}")
        return {"error": str(e)}

# Database dependencies for FastAPI
def get_db() -> Client:
    """Dependency to inject database client into FastAPI endpoints"""
    return get_supabase_client()

def get_admin_db() -> Client:
    """Dependency to inject admin database client into FastAPI endpoints"""
    return get_supabase_admin_client()
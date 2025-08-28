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


async def get_dashboard_stats() -> Dict:
    """Get dashboard statistics for admin"""
    try:
        admin_client = get_supabase_admin_client()
        
        # Count total projects
        projects_response = admin_client.from_("projects").select("id", count="exact").execute()
        total_projects = projects_response.count or 0
        
        # Count active projects (in_development status)
        active_projects_response = admin_client.from_("projects").select("id", count="exact").eq("status", "in_development").execute()
        active_projects = active_projects_response.count or 0
        
        # Count total clients
        clients_response = admin_client.from_("users").select("id", count="exact").eq("role", "client").execute()
        total_clients = clients_response.count or 0
        
        # Count open tickets (to_read, processing)
        open_tickets_response = admin_client.from_("tickets").select("id", count="exact").in_("status", ["to_read", "processing"]).execute()
        open_tickets = open_tickets_response.count or 0
        
        # Count active tasks (in_progress)
        active_tasks_response = admin_client.from_("tasks").select("id", count="exact").eq("status", "in_progress").execute()
        active_tasks = active_tasks_response.count or 0
        
        # Count total staff
        staff_response = admin_client.from_("users").select("id", count="exact").eq("role", "internal_staff").execute()
        total_staff = staff_response.count or 0
        
        return {
            "projects": {
                "total": total_projects,
                "active": active_projects,
                "completed": total_projects - active_projects
            },
            "clients": {
                "total": total_clients
            },
            "staff": {
                "total": total_staff
            },
            "tickets": {
                "open": open_tickets
            },
            "tasks": {
                "active": active_tasks
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {str(e)}")
        return {
            "projects": {"total": 0, "active": 0, "completed": 0},
            "clients": {"total": 0},
            "staff": {"total": 0},
            "tickets": {"open": 0},
            "tasks": {"active": 0}
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


async def create_tasks_bulk(ticket_id: str, tasks: List[Dict]) -> Dict:
    """Create multiple tasks for a ticket (admin only). Also set ticket status to 'accepted'"""
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
            action = t.get("action")
            assigned_to = t.get("assigned_to")
            priority = t.get("priority", "medium")

            if not action or not assigned_to:
                return {"error": "Each task must include 'action' and 'assigned_to'"}
            if priority not in valid_priorities:
                return {"error": f"Invalid priority '{priority}'. Allowed: {list(valid_priorities)}"}

            # Validate assigned user exists
            user_check = admin_client.from_("users").select("id").eq("id", assigned_to).single().execute()
            if not user_check.data:
                return {"error": f"Assigned user not found: {assigned_to}"}

            insert_payload.append({
                "ticket_id": ticket_id,
                "assigned_to": assigned_to,
                "action": action,
                "priority": priority,
                "status": "in_progress"
            })

        if not insert_payload:
            return {"error": "No valid tasks to create"}

        # Insert tasks in bulk
        response = admin_client.from_("tasks").insert(insert_payload).execute()
        created = response.data if response.data else []

        # Update ticket status to accepted
        admin_client.from_("tickets").update({"status": "accepted"}).eq("id", ticket_id).execute()

        return {"tasks": created, "ticket_id": ticket_id, "ticket_status": "accepted"}

    except Exception as e:
        logger.error(f"Error creating tasks bulk for ticket {ticket_id}: {str(e)}")
        return {"error": str(e)}

def create_project(name: str, client_id: str, website: str = None, socials: str = None):
    """
    Create a new project in the database
    
    Args:
        name: Project name (required)
        client_id: ID of the client who owns the project (required)
        website: Project website URL (optional)
        socials: Project social media info (optional)
    
    Returns:
        dict: Created project data or error message
    """
    try:
        admin_client = get_supabase_admin_client()
        
        # Verify client exists
        client_check = admin_client.from_("users").select("id, role").eq("id", client_id).single().execute()
        if not client_check.data:
            return {"error": "Client not found"}
        
        # Verify the user is actually a client
        if client_check.data.get("role") != "client":
            return {"error": "Specified user is not a client"}
        
        # Prepare project data
        project_data = {
            "name": name,
            "client_id": client_id,
            "status": "in_development"
        }
        
        # Add optional fields if provided
        if website:
            project_data["website_url"] = website
        if socials:
            project_data["social_links"] = socials
            
        # Insert the project
        response = admin_client.from_("projects").insert(project_data).execute()
        
        if response.data:
            logger.info(f"Project created successfully: {response.data[0].get('id')}")
            return {"project": response.data[0]}
        else:
            return {"error": "Failed to create project"}
            
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}")
        return {"error": str(e)}

async def get_all_projects_with_relations() -> List[Dict]:
    """Return all projects with related client, tickets and tasks (admin client)."""
    try:
        admin_client = get_supabase_admin_client()
        
        # Get projects
        projects_response = admin_client.from_("projects").select("*").order("created_at", desc=True).execute()
        projects = projects_response.data if projects_response.data else []
        
        # For each project, get client and tickets separately
        for project in projects:
            # Get client info
            if project.get("client_id"):
                client_response = admin_client.from_("users").select("id, email, username, full_name").eq("id", project["client_id"]).single().execute()
                project["client"] = client_response.data if client_response.data else {
                    "id": None,
                    "email": "Unknown Client",
                    "username": "unknown", 
                    "full_name": "Unknown Client"
                }
            else:
                project["client"] = {
                    "id": None,
                    "email": "Unknown Client",
                    "username": "unknown",
                    "full_name": "Unknown Client"
                }
            
            # Get tickets for this project
            tickets_response = admin_client.from_("tickets").select("*").eq("project_id", project["id"]).execute()
            tickets = tickets_response.data if tickets_response.data else []
            
            # For each ticket, get tasks
            for ticket in tickets:
                tasks_response = admin_client.from_("tasks").select("*").eq("ticket_id", ticket["id"]).execute()
                ticket["tasks"] = tasks_response.data if tasks_response.data else []
            
            project["tickets"] = tickets
        
        return projects
    except Exception as e:
        logger.error(f"Error fetching projects with relations: {str(e)}")
        return []

async def get_project_with_relations(project_id: str) -> Optional[Dict]:
    """Return single project with related client, tickets and tasks (admin client)."""
    try:
        admin_client = get_supabase_admin_client()
        
        # Get project
        project_response = admin_client.from_("projects").select("*").eq("id", project_id).single().execute()
        if not project_response.data:
            return None
        
        project = project_response.data
        
        # Get client info
        if project.get("client_id"):
            client_response = admin_client.from_("users").select("id, email, username, full_name").eq("id", project["client_id"]).single().execute()
            project["client"] = client_response.data if client_response.data else {
                "id": None,
                "email": "Unknown Client", 
                "username": "unknown",
                "full_name": "Unknown Client"
            }
        else:
            project["client"] = {
                "id": None,
                "email": "Unknown Client",
                "username": "unknown",
                "full_name": "Unknown Client"
            }
        
        # Get tickets for this project
        tickets_response = admin_client.from_("tickets").select("*").eq("project_id", project["id"]).execute()
        tickets = tickets_response.data if tickets_response.data else []
        
        # For each ticket, get tasks
        for ticket in tickets:
            tasks_response = admin_client.from_("tasks").select("*").eq("ticket_id", ticket["id"]).execute()
            ticket["tasks"] = tasks_response.data if tasks_response.data else []
        
        project["tickets"] = tickets
        
        return project
    except Exception as e:
        logger.error(f"Error fetching project {project_id}: {str(e)}")
        return None

async def get_users_by_role_with_projects(role: str) -> List[Dict]:
    """Get users by role with project counts (for clients)"""
    try:
        admin_client = get_supabase_admin_client()
        
        # Get users by role
        response = admin_client.from_("users").select("*").eq("role", role).order("created_at").execute()
        users = response.data if response.data else []
        
        # Add project counts for each user (only for clients)
        for user in users:
            if role == "client":
                # Count projects for this client
                projects_response = admin_client.from_("projects").select("id", count="exact").eq("client_id", user["id"]).execute()
                user["projects_count"] = projects_response.count if projects_response.count else 0
                
            else:
                user["projects_count"] = 0
                       
        return users
        
    except Exception as e:
        logger.error(f"Error fetching users with role {role}: {str(e)}")
        return []


async def get_client_projects(client_id: str) -> List[Dict]:
    """Get projects for a specific client"""
    try:
        admin_client = get_supabase_admin_client()
        
        # Get projects for this client
        projects_response = admin_client.from_("projects").select("*").eq("client_id", client_id).order("created_at", desc=True).execute()
        projects = projects_response.data if projects_response.data else []
        
        # For each project, get basic ticket counts
        for project in projects:
            # Count total tickets for this project
            tickets_response = admin_client.from_("tickets").select("id", count="exact").eq("project_id", project["id"]).execute()
            project["tickets_count"] = tickets_response.count if tickets_response.count else 0
            
            # Count open tickets for this project
            open_tickets_response = admin_client.from_("tickets").select("id", count="exact").eq("project_id", project["id"]).in_("status", ["to_read", "processing"]).execute()
            project["open_tickets_count"] = open_tickets_response.count if open_tickets_response.count else 0
        
        return projects
        
    except Exception as e:
        logger.error(f"Error fetching projects for client {client_id}: {str(e)}")
        return []

async def create_ticket(project_id: str, client_id: str, message: str) -> Dict:
    """Create a new ticket for a project (client only)"""
    try:
        admin_client = get_supabase_admin_client()
        
        # Verify project exists and belongs to the client
        project_check = admin_client.from_("projects").select("id, client_id, name").eq("id", project_id).single().execute()
        if not project_check.data:
            return {"error": "Project not found"}
        
        if project_check.data.get("client_id") != client_id:
            return {"error": "You can only create tickets for your own projects"}
        
        # Create ticket data
        ticket_data = {
            "project_id": project_id,
            "client_id": client_id,
            "message": message,
            "status": "to_read"  # Default status for new tickets
        }
        
        # Insert the ticket
        response = admin_client.from_("tickets").insert(ticket_data).execute()
        
        if response.data:
            logger.info(f"Ticket created successfully: {response.data[0].get('id')}")
            return {"ticket": response.data[0]}
        else:
            return {"error": "Failed to create ticket"}
            
    except Exception as e:
        logger.error(f"Error creating ticket: {str(e)}")
        return {"error": str(e)}

async def get_client_tickets(client_id: str, project_id: str = None) -> List[Dict]:
    """Get tickets for a client, optionally filtered by project, with task details"""
    try:
        admin_client = get_supabase_admin_client()
        
        # Build query
        query = admin_client.from_("tickets").select("""
            id,
            project_id,
            message,
            status,
            created_at,
            updated_at,
            projects:project_id (
                id,
                name,
                status
            )
        """).eq("client_id", client_id)
        
        # Filter by project if specified
        if project_id:
            query = query.eq("project_id", project_id)
        
        response = query.order("created_at", desc=True).execute()
        tickets = response.data if response.data else []
        
        # For each ticket, get task details
        for ticket in tickets:
            # Get tasks with assigned user info
            tasks_response = admin_client.from_("tasks").select("""
                id,
                action,
                priority,
                status,
                created_at,
                updated_at,
                users:assigned_to (
                    full_name,
                    username
                )
            """).eq("ticket_id", ticket["id"]).order("created_at", desc=True).execute()
            
            tasks = tasks_response.data if tasks_response.data else []
            
            # Format tasks for client view
            formatted_tasks = []
            for task in tasks:
                assigned_user = task.get("users") or {}
                formatted_task = {
                    "id": task.get("id"),
                    "action": task.get("action"),
                    "priority": task.get("priority"),
                    "status": task.get("status"),
                    "assigned_to": {
                        "name": assigned_user.get("full_name") or "Staff Member",
                        "username": assigned_user.get("username") or "staff"
                    },
                    "created_at": task.get("created_at"),
                    "updated_at": task.get("updated_at")
                }
                formatted_tasks.append(formatted_task)
            
            # Add task statistics
            ticket["tasks"] = formatted_tasks
            ticket["tasks_count"] = len(formatted_tasks)
            ticket["completed_tasks"] = len([t for t in formatted_tasks if t["status"] == "completed"])
            ticket["active_tasks"] = len([t for t in formatted_tasks if t["status"] == "in_progress"])
        
        return tickets
        
    except Exception as e:
        logger.error(f"Error fetching tickets for client {client_id}: {str(e)}")
        return []


async def get_client_ticket_with_tasks(client_id: str, ticket_id: str) -> Optional[Dict]:
    """Get a specific ticket with its tasks for a client"""
    try:
        admin_client = get_supabase_admin_client()
        
        # Get ticket and verify ownership
        ticket_response = admin_client.from_("tickets").select("""
            id,
            project_id,
            message,
            status,
            created_at,
            updated_at,
            projects:project_id (
                id,
                name,
                status
            )
        """).eq("id", ticket_id).eq("client_id", client_id).single().execute()
        
        if not ticket_response.data:
            return None
        
        ticket = ticket_response.data
        
        # Get tasks for this ticket with assigned user details
        tasks_response = admin_client.from_("tasks").select("""
            id,
            action,
            priority,
            status,
            created_at,
            updated_at,
            users:assigned_to (
                id,
                full_name,
                username,
                email
            )
        """).eq("ticket_id", ticket_id).order("created_at", desc=True).execute()
        
        tasks = tasks_response.data if tasks_response.data else []
        
        # Format tasks for client view (hide sensitive info)
        formatted_tasks = []
        for task in tasks:
            assigned_user = task.get("users") or {}
            formatted_task = {
                "id": task.get("id"),
                "action": task.get("action"),
                "priority": task.get("priority"),
                "status": task.get("status"),
                "assigned_to": {
                    "name": assigned_user.get("full_name") or "Staff Member",
                    "username": assigned_user.get("username") or "staff"
                    # Hide email for privacy
                },
                "created_at": task.get("created_at"),
                "updated_at": task.get("updated_at")
            }
            formatted_tasks.append(formatted_task)
        
        ticket["tasks"] = formatted_tasks
        ticket["tasks_count"] = len(formatted_tasks)
        ticket["completed_tasks"] = len([t for t in formatted_tasks if t["status"] == "completed"])
        ticket["active_tasks"] = len([t for t in formatted_tasks if t["status"] == "in_progress"])
        
        return ticket
        
    except Exception as e:
        logger.error(f"Error fetching ticket {ticket_id} for client {client_id}: {str(e)}")
        return None

# TASK MANAGEMENT

async def start_task_timer(task_id: str, user_id: str) -> Dict:
    """Start a timer for a task (staff only)"""
    try:
        admin_client = get_supabase_admin_client()
        
        # Verify task exists and user has permission
        task_check = admin_client.from_("tasks").select("assigned_to, time_logs").eq("id", task_id).single().execute()
        
        if not task_check.data:
            return {"error": "Task not found"}
        
        # Check if user is assigned to this task or is admin
        user_role_check = admin_client.from_("users").select("role").eq("id", user_id).single().execute()
        user_role = user_role_check.data.get("role") if user_role_check.data else None
        
        if task_check.data["assigned_to"] != user_id and user_role != "admin":
            return {"error": "Permission denied"}
        
        # Check if there's already an active session (no end_time)
        time_logs = task_check.data.get("time_logs") or []
        active_session = next((log for log in time_logs if not log.get("end_time")), None)
        
        if active_session:
            return {"error": "Task timer is already running"}
        
        # Add new session start
        from datetime import datetime
        start_time = datetime.utcnow().isoformat()
        
        new_session = {
            "start_time": start_time,
            "started_by": user_id
        }
        
        time_logs.append(new_session)
        
        # Update task
        response = admin_client.from_("tasks").update({
            "time_logs": time_logs,
            "status": "in_progress"  # Auto-start task when timer starts
        }).eq("id", task_id).execute()
        
        if response.data:
            logger.info(f"Timer started for task {task_id} by user {user_id}")
            return {"session": new_session, "task_id": task_id}
        else:
            return {"error": "Failed to start timer"}
            
    except Exception as e:
        logger.error(f"Error starting task timer: {str(e)}")
        return {"error": str(e)}


async def stop_task_timer(task_id: str, user_id: str) -> Dict:
    """Stop a timer for a task (staff only)"""
    try:
        admin_client = get_supabase_admin_client()
        
        # Verify task exists and user has permission
        task_check = admin_client.from_("tasks").select("assigned_to, time_logs").eq("id", task_id).single().execute()
        
        if not task_check.data:
            return {"error": "Task not found"}
        
        # Check permission
        user_role_check = admin_client.from_("users").select("role").eq("id", user_id).single().execute()
        user_role = user_role_check.data.get("role") if user_role_check.data else None
        
        if task_check.data["assigned_to"] != user_id and user_role != "admin":
            return {"error": "Permission denied"}
        
        # Find active session
        time_logs = task_check.data.get("time_logs") or []
        active_session_index = next(
            (i for i, log in enumerate(time_logs) if not log.get("end_time")), 
            None
        )
        
        if active_session_index is None:
            return {"error": "No active timer found"}
        
        # Complete the session
        from datetime import datetime
        end_time = datetime.utcnow().isoformat()
        start_time = time_logs[active_session_index]["start_time"]
        
        # Calculate duration
        from datetime import datetime
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        duration_minutes = int((end_dt - start_dt).total_seconds() / 60)
        
        # Update session
        time_logs[active_session_index].update({
            "end_time": end_time,
            "duration_minutes": duration_minutes,
            "completed_by": user_id
        })
        
        # Calculate totals
        total_minutes = sum(log.get("duration_minutes", 0) for log in time_logs if log.get("duration_minutes"))
        sessions_count = len([log for log in time_logs if log.get("end_time")])
        
        # Update task
        response = admin_client.from_("tasks").update({
            "time_logs": time_logs,
            "total_time_minutes": total_minutes,
            "time_sessions_count": sessions_count
        }).eq("id", task_id).execute()
        
        if response.data:
            logger.info(f"Timer stopped for task {task_id} by user {user_id}. Duration: {duration_minutes} minutes")
            return {
                "session": time_logs[active_session_index],
                "task_id": task_id,
                "total_time_minutes": total_minutes,
                "sessions_count": sessions_count
            }
        else:
            return {"error": "Failed to stop timer"}
            
    except Exception as e:
        logger.error(f"Error stopping task timer: {str(e)}")
        return {"error": str(e)}

async def get_task_time_logs(task_id: str, user_id: str) -> Dict:
    """Get time logs for a task (staff/admin only)"""
    try:
        admin_client = get_supabase_admin_client()
        
        # Get task with time logs
        task_response = admin_client.from_("tasks").select("""
            id,
            action,
            assigned_to,
            status,
            time_logs,
            total_time_minutes,
            time_sessions_count,
            users:assigned_to (
                full_name,
                username
            )
        """).eq("id", task_id).single().execute()
        
        if not task_response.data:
            return {"error": "Task not found"}
        
        task = task_response.data
        
        # Check permission
        user_role_check = admin_client.from_("users").select("role").eq("id", user_id).single().execute()
        user_role = user_role_check.data.get("role") if user_role_check.data else None
        
        if task["assigned_to"] != user_id and user_role not in ["admin", "internal_staff"]:
            return {"error": "Permission denied"}
        
        time_logs = task.get("time_logs") or []
        
        # Check for active session
        active_session = next((log for log in time_logs if not log.get("end_time")), None)
        
        return {
            "task_id": task_id,
            "task_action": task.get("action"),
            "assigned_to": task.get("users", {}),
            "time_logs": time_logs,
            "active_session": active_session,
            "summary": {
                "total_time_minutes": task.get("total_time_minutes", 0),
                "total_time_hours": round(task.get("total_time_minutes", 0) / 60, 2),
                "sessions_count": task.get("time_sessions_count", 0),
                "is_timer_running": active_session is not None
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting task time logs: {str(e)}")
        return {"error": str(e)}


async def get_client_active_timers(client_id: str) -> Dict:
    """Get all active timers for tasks in client's projects"""
    try:
        admin_client = get_supabase_admin_client()
        
        # Get all projects for this client
        projects_response = admin_client.from_("projects").select("id").eq("client_id", client_id).execute()
        
        if not projects_response.data:
            return {
                "client_id": client_id,
                "active_timers": [],
                "total_active_timers": 0
            }
        
        project_ids = [project["id"] for project in projects_response.data]
        
        # Get all tickets for client's projects
        tickets_response = admin_client.from_("tickets").select("id").in_("project_id", project_ids).execute()
        
        if not tickets_response.data:
            return {
                "client_id": client_id,
                "active_timers": [],
                "total_active_timers": 0
            }
        
        ticket_ids = [ticket["id"] for ticket in tickets_response.data]
        
        # Get all tasks for these tickets with time logs
        tasks_response = admin_client.from_("tasks").select("""
            id,
            action,
            time_logs,
            assigned_to,
            users:assigned_to (
                full_name,
                username
            ),
            tickets!inner (
                id,
                message,
                projects!inner (
                    id,
                    name
                )
            )
        """).in_("ticket_id", ticket_ids).execute()
        
        if not tasks_response.data:
            return {
                "client_id": client_id,
                "active_timers": [],
                "total_active_timers": 0
            }
        
        active_timers = []
        
        # Check each task for active timers
        for task in tasks_response.data:
            time_logs = task.get("time_logs", [])
            if not time_logs:
                continue
            
            # Find active session (end_time is null)
            for session in time_logs:
                if session.get("end_time") is None and session.get("start_time"):
                    user_info = task.get("users") or {}
                    ticket_info = task.get("tickets") or {}
                    project_info = ticket_info.get("projects") or {}
                    
                    active_timers.append({
                        "task_id": task.get("id"),
                        "task_action": task.get("action"),
                        "start_time": session.get("start_time"),
                        "session_id": session.get("session_id"),
                        "user_id": session.get("user_id"),
                        "user_name": user_info.get("full_name") or user_info.get("username") or "Staff Member",
                        "user_username": user_info.get("username"),
                        "project": {
                            "id": project_info.get("id"),
                            "name": project_info.get("name")
                        },
                        "ticket": {
                            "id": ticket_info.get("id"),
                            "message": ticket_info.get("message")
                        }
                    })
                    break  # Only one active session per task
        
        return {
            "client_id": client_id,
            "active_timers": active_timers,
            "total_active_timers": len(active_timers),
            "projects_checked": len(project_ids),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting client active timers: {str(e)}")
        return {"error": str(e)}


# Database dependencies for FastAPI
def get_db() -> Client:
    """Dependency to inject database client into FastAPI endpoints"""
    return get_supabase_client()

def get_admin_db() -> Client:
    """Dependency to inject admin database client into FastAPI endpoints"""
    return get_supabase_admin_client()
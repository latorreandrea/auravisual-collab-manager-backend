from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from config import settings, get_app_config, get_cors_config, get_server_config
from supabase import create_client
from utils.auth import get_current_user, require_admin, require_admin_or_staff
from typing import Dict
from datetime import datetime

from database import (
    test_connection, get_db, get_all_users, 
    get_users_by_role, get_users_by_role_with_tasks,  
    get_user_task_counts, get_tasks_by_user, update_task_status,
    Client, get_supabase_client, create_task,
    get_supabase_admin_client, get_user_by_id,
    get_all_projects_with_relations, get_project_with_relations,
    create_tasks_bulk, create_project, get_users_by_role_with_projects,
    get_dashboard_stats, get_client_projects, create_ticket, get_client_tickets,
    get_client_ticket_with_tasks, start_task_timer, stop_task_timer, get_task_time_logs
)

# Initialize FastAPI app with centralized configuration
app = FastAPI(**get_app_config())

# Add CORS middleware
app.add_middleware(CORSMiddleware, **get_cors_config())


# MAIN VARIABLES SETTINGS:

OPEN_TICKET_STATUSES = {"to_read", "processing"}
ACTIVE_TASK_STATUS = "in_progress"


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
    """List all clients with project counts (admin/staff only)"""
    clients = await get_users_by_role_with_projects("client")
    
    # Format response to include project information
    formatted_clients = []
    for client in clients:
        formatted_client = {
            "id": client.get("id"),
            "email": client.get("email"),
            "username": client.get("username"),
            "full_name": client.get("full_name"),
            "role": client.get("role"),
            "is_active": client.get("is_active"),
            "created_at": client.get("created_at"),
            "projects_count": client.get("projects_count", 0),
        }
        formatted_clients.append(formatted_client)
    
    return {
        "total_clients": len(formatted_clients),
        "clients": formatted_clients,
        "requested_by": current_user.get("username")
    }


@app.get("/admin/dashboard")
async def admin_dashboard(current_user: Dict = Depends(require_admin)):
    """Get dashboard statistics (admin only)"""
    stats = await get_dashboard_stats()
    
    return {
        "dashboard": stats,
        "summary": {
            "total_active_projects": stats["projects"]["active"],
            "total_clients": stats["clients"]["total"],
            "open_tickets": stats["tickets"]["open"],
            "active_tasks": stats["tasks"]["active"],
            "total_staff": stats["staff"]["total"]
        },
        "requested_by": current_user.get("username"),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/admin/users/staff")
async def list_internal_staff(current_user: Dict = Depends(require_admin)):
    """List all internal staff with task statistics (admin only)"""
    staff = await get_users_by_role_with_tasks("internal_staff")
    
    # Format response to include only required fields
    formatted_staff = []
    for member in staff:
        formatted_member = {
            "id": member.get("id"),
            "email": member.get("email"),
            "username": member.get("username"),
            "full_name": member.get("full_name"),
            "task_counts": member.get("task_counts", {
                "total_assigned": 0,
                "active_tasks": 0
            })
        }
        formatted_staff.append(formatted_member)
    
    return {
        "total_staff": len(formatted_staff),
        "staff": formatted_staff
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


# PROJECTS API:
@app.get("/admin/projects")
async def admin_list_projects(current_user: Dict = Depends(require_admin)):
    """List all projects with client and only open tickets + active tasks (admin only)."""
    projects = await get_all_projects_with_relations()
    formatted = []
    for p in projects:
        client = p.get("client") or {}
        tickets = p.get("tickets") or []
        
        # Filter open tickets
        open_tickets = []
        open_tasks_count = 0
        for t in tickets:
            if t.get("status") in OPEN_TICKET_STATUSES:
                tasks = t.get("tasks") or []
                active_tasks = [task for task in tasks if task.get("status") == ACTIVE_TASK_STATUS]
                t_copy = {
                    "id": t.get("id"),
                    "message": t.get("message"),
                    "status": t.get("status"),
                    "created_at": t.get("created_at"),
                    "updated_at": t.get("updated_at"),
                    "active_tasks": active_tasks,
                    "active_tasks_count": len(active_tasks)
                }
                open_tasks_count += len(active_tasks)
                open_tickets.append(t_copy)
        
        formatted.append({
            "id": p.get("id"),
            "name": p.get("name") or "Unnamed Project",  
            "description": p.get("description") or "",   
            "status": p.get("status"),
            "plan": p.get("plan"),
            "website": p.get("website_url") or "",
            "socials": p.get("social_links") or [],        
            "contract_subscription_date": p.get("contract_subscription_date"), 
            "client": {
                "id": client.get("id"),
                "email": client.get("email") or "unknown@example.com",
                "username": client.get("username") or "unknown",
                "full_name": client.get("full_name") or "Unknown Client"
            },
            "open_tickets_count": len(open_tickets),
            "open_tasks_count": open_tasks_count,
            "open_tickets": open_tickets,
            "created_at": p.get("created_at"),
            "updated_at": p.get("updated_at")
        })
    
    return {
        "total_projects": len(formatted),
        "projects": formatted,
        "requested_by": current_user.get("username")
    }

@app.get("/admin/projects/{project_id}")
async def admin_get_project(project_id: str, current_user: Dict = Depends(require_admin)):
    """Get single project with client and only open tickets + active tasks (admin only)."""
    p = await get_project_with_relations(project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    client = p.get("client") or {}
    tickets = p.get("tickets") or []
    open_tickets = []
    open_tasks_count = 0
    for t in tickets:
        if t.get("status") in OPEN_TICKET_STATUSES:
            tasks = t.get("tasks") or []
            active_tasks = [task for task in tasks if task.get("status") == ACTIVE_TASK_STATUS]
            t_copy = {
                "id": t.get("id"),
                "message": t.get("message"),
                "status": t.get("status"),
                "created_at": t.get("created_at"),
                "updated_at": t.get("updated_at"),
                "active_tasks": active_tasks,
                "active_tasks_count": len(active_tasks)
            }
            open_tasks_count += len(active_tasks)
            open_tickets.append(t_copy)
    result = {
        "id": p.get("id"),
        "name": p.get("name"),
        "description": p.get("description"),
        "status": p.get("status"),
        "plan": p.get("plan"),
        "website": p.get("website_url"),
        "socials": p.get("social_links"),
        "contract_subscription_date": p.get("contract_subscription_date"),
        "client": {
            "id": client.get("id"),
            "email": client.get("email"),
            "username": client.get("username"),
            "full_name": client.get("full_name")
        },
        "open_tickets_count": len(open_tickets),
        "open_tasks_count": open_tasks_count,
        "open_tickets": open_tickets,
        "created_at": p.get("created_at"),
        "updated_at": p.get("updated_at"),
        "requested_by": current_user.get("username")
    }
    return result

# PROFILE API


# TASK API
@app.get("/tasks/my")
async def get_my_tasks(
    status: str = None,
    current_user: Dict = Depends(get_current_user)
):
    """Get tasks assigned to current user with optional status filter"""
    user_id = current_user.get("id")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found")
    
    # Validate status filter if provided
    if status and status not in ["in_progress", "completed"]:
        raise HTTPException(status_code=400, detail="Invalid status. Must be 'in_progress' or 'completed'")
    
    tasks = await get_tasks_by_user(user_id, status)
    
    return {
        "user_id": user_id,
        "status_filter": status or "all",
        "total_tasks": len(tasks),
        "tasks": tasks
    }

@app.get("/tasks/my/active")
async def get_my_active_tasks(current_user: Dict = Depends(get_current_user)):
    """Get only active (in_progress) tasks for current user"""
    user_id = current_user.get("id")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found")
    
    tasks = await get_tasks_by_user(user_id, "in_progress")
    
    return {
        "user_id": user_id,
        "active_tasks": len(tasks),
        "tasks": tasks
    }

@app.patch("/tasks/{task_id}/status")
async def update_task_status_endpoint(
    task_id: str,
    status_data: dict,
    current_user: Dict = Depends(get_current_user)
):
    """Update task status (only by assigned user or admin)"""
    new_status = status_data.get("status")
    
    if not new_status:
        raise HTTPException(status_code=400, detail="Status is required")
    
    if new_status not in ["in_progress", "completed"]:
        raise HTTPException(status_code=400, detail="Invalid status. Must be 'in_progress' or 'completed'")
    
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found")
    
    result = await update_task_status(task_id, new_status, user_id)
    
    if "error" in result:
        if result["error"] == "Permission denied":
            raise HTTPException(status_code=403, detail=result["error"])
        elif result["error"] == "Task not found":
            raise HTTPException(status_code=404, detail=result["error"])
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    
    return {
        "message": "Task status updated successfully",
        "task_id": task_id,
        "new_status": new_status,
        "updated_by": current_user.get("username")
    }


# TASK ADMIN API
@app.get("/admin/tasks")
async def get_all_tasks(
    status: str = None,
    assigned_to: str = None,
    current_user: Dict = Depends(require_admin)
):
    """Get all tasks with optional filters (admin only)"""
    try:
        admin_client = get_supabase_admin_client()
        
        query = admin_client.from_("tasks").select("""
            id,
            ticket_id,
            assigned_to,
            action,
            priority,
            status,
            created_at,
            updated_at,
            users:assigned_to (
                full_name,
                email,
                username
            ),
            tickets:ticket_id (
                id,
                message,
                status,
                projects:project_id (
                    id,
                    name
                )
            )
        """)
        
        if status:
            query = query.eq("status", status)
        
        if assigned_to:
            query = query.eq("assigned_to", assigned_to)
        
        response = query.order("created_at", desc=True).execute()
        tasks = response.data if response.data else []
        
        return {
            "total_tasks": len(tasks),
            "filters": {
                "status": status,
                "assigned_to": assigned_to
            },
            "tasks": tasks,
            "requested_by": current_user.get("username")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tasks: {str(e)}")

@app.post("/admin/tasks")
async def create_task_endpoint(
    task_data: dict,
    current_user: Dict = Depends(require_admin)
):
    """Create a new task (admin only)"""
    try:
        # Extract data from request
        ticket_id = task_data.get("ticket_id")
        assigned_to = task_data.get("assigned_to") 
        action = task_data.get("action")
        priority = task_data.get("priority", "medium")
        
        # Validate required fields
        if not all([ticket_id, assigned_to, action]):
            raise HTTPException(
                status_code=400,
                detail="ticket_id, assigned_to, and action are required"
            )
        
        # Validate priority
        valid_priorities = ["low", "medium", "high", "urgent"]
        if priority not in valid_priorities:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid priority. Must be one of: {valid_priorities}"
            )
        
        # Create task
        result = await create_task(ticket_id, assigned_to, action, priority)
        
        if "error" in result:
            raise HTTPException(
                status_code=400,
                detail=result["error"]
            )
        
        return {
            "message": "Task created successfully",
            "task": result,
            "created_by": current_user.get("username")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating task: {str(e)}"
        )


@app.post("/admin/tickets/{ticket_id}/tasks")
async def admin_create_tasks_for_ticket(
    ticket_id: str,
    payload: dict,
    current_user: Dict = Depends(require_admin)
):
    """
    Create multiple tasks for a ticket (admin only).
    Request body: {"tasks": [{"action": "...", "assigned_to": "...", "priority": "medium"}, ...]}
    Ticket will be moved to 'processing'.
    """
    tasks = payload.get("tasks")
    if not tasks or not isinstance(tasks, list):
        raise HTTPException(status_code=400, detail="Request body must include 'tasks' array")

    # Minimal validation occurs in DB helper; call it
    result = await create_tasks_bulk(ticket_id, tasks)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return {
        "message": "Tasks created and ticket moved to 'processing'",
        "created_tasks_count": len(result.get("tasks", [])),
        "created_tasks": result.get("tasks", []),
        "ticket_id": ticket_id,
        "ticket_status": result.get("ticket_status"),
        "created_by": current_user.get("username")
    }

@app.post("/admin/projects")
async def create_project_endpoint(
    project_data: dict,
    current_user: Dict = Depends(require_admin)
):
    """Create a new project (admin only)"""
    try:
        # Extract data from request
        name = project_data.get("name")
        client_id = project_data.get("client_id")
        website = project_data.get("website")  # Optional
        socials = project_data.get("socials")  # Optional
        
        # Validate required fields
        if not name or not client_id:
            raise HTTPException(
                status_code=400,
                detail="name and client_id are required"
            )
        
        # Create project using database function
        result = create_project(
            name=name,
            client_id=client_id,
            website=website,
            socials=socials
        )
        
        # Check for errors
        if "error" in result:
            if "not found" in result["error"]:
                raise HTTPException(status_code=404, detail=result["error"])
            elif "not a client" in result["error"]:
                raise HTTPException(status_code=400, detail=result["error"])
            else:
                raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "message": "Project created successfully",
            "project": result.get("project"),
            "created_by": current_user.get("username")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating project: {str(e)}")

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

# CLIENT API - PROJECTS AND TICKETS
@app.get("/client/projects")
async def client_list_projects(current_user: Dict = Depends(get_current_user)):
    """List projects for the current client"""
    user_role = current_user.get("role")
    if user_role != "client":
        raise HTTPException(status_code=403, detail="Only clients can access this endpoint")
    
    client_id = current_user.get("id")
    projects = await get_client_projects(client_id)
    
    # Format response
    formatted_projects = []
    for project in projects:
        formatted_project = {
            "id": project.get("id"),
            "name": project.get("name"),
            "description": project.get("description"),
            "status": project.get("status"),
            "plan": project.get("plan"),
            "website": project.get("website_url"),
            "socials": project.get("social_links"),
            "contract_subscription_date": project.get("contract_subscription_date"),
            "tickets_count": project.get("tickets_count", 0),
            "open_tickets_count": project.get("open_tickets_count", 0),
            "created_at": project.get("created_at"),
            "updated_at": project.get("updated_at")
        }
        formatted_projects.append(formatted_project)
    
    return {
        "total_projects": len(formatted_projects),
        "projects": formatted_projects,
        "client_id": client_id,
        "requested_by": current_user.get("username")
    }

@app.post("/client/projects/{project_id}/tickets")
async def client_create_ticket(
    project_id: str,
    ticket_data: dict,
    current_user: Dict = Depends(get_current_user)
):
    """Create a new ticket for a project (client only)"""
    try:
        # Verify user is a client
        user_role = current_user.get("role")
        if user_role != "client":
            raise HTTPException(status_code=403, detail="Only clients can create tickets")
        
        # Extract and validate data
        message = ticket_data.get("message")
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        if len(message.strip()) < 10:
            raise HTTPException(status_code=400, detail="Message must be at least 10 characters long")
        
        client_id = current_user.get("id")
        
        # Create ticket
        result = await create_ticket(project_id, client_id, message.strip())
        
        if "error" in result:
            if "not found" in result["error"]:
                raise HTTPException(status_code=404, detail=result["error"])
            elif "your own projects" in result["error"]:
                raise HTTPException(status_code=403, detail=result["error"])
            else:
                raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "message": "Ticket created successfully",
            "ticket": result.get("ticket"),
            "project_id": project_id,
            "created_by": current_user.get("username")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating ticket: {str(e)}")

@app.get("/client/tickets")
async def client_list_tickets(
    project_id: str = None,
    current_user: Dict = Depends(get_current_user)
):
    """List tickets for the current client with task details, optionally filtered by project"""
    user_role = current_user.get("role")
    if user_role != "client":
        raise HTTPException(status_code=403, detail="Only clients can access this endpoint")
    
    client_id = current_user.get("id")
    tickets = await get_client_tickets(client_id, project_id)
    
    # Format response 
    formatted_tickets = []
    for ticket in tickets:
        project_info = ticket.get("projects") or {}
        formatted_ticket = {
            "id": ticket.get("id"),
            "message": ticket.get("message"),
            "status": ticket.get("status"),
            "project": {
                "id": project_info.get("id"),
                "name": project_info.get("name"),
                "status": project_info.get("status")
            },
            "tasks": ticket.get("tasks", []),  
            "tasks_summary": {
                "total": ticket.get("tasks_count", 0),
                "active": ticket.get("active_tasks", 0),
                "completed": ticket.get("completed_tasks", 0)
            },
            "created_at": ticket.get("created_at"),
            "updated_at": ticket.get("updated_at")
        }
        formatted_tickets.append(formatted_ticket)
    
    return {
        "total_tickets": len(formatted_tickets),
        "tickets": formatted_tickets,
        "project_filter": project_id,
        "client_id": client_id,
        "requested_by": current_user.get("username")
    }

@app.get("/client/projects/{project_id}")
async def client_get_project(
    project_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get single project details for the current client"""
    user_role = current_user.get("role")
    if user_role != "client":
        raise HTTPException(status_code=403, detail="Only clients can access this endpoint")
    
    client_id = current_user.get("id")
    
    try:
        admin_client = get_supabase_admin_client()
        
        # Get project and verify ownership
        project_response = admin_client.from_("projects").select("*").eq("id", project_id).eq("client_id", client_id).single().execute()
        
        if not project_response.data:
            raise HTTPException(status_code=404, detail="Project not found or access denied")
        
        project = project_response.data
        
        # Get tickets for this project
        tickets = await get_client_tickets(client_id, project_id)
        
        # Format response
        formatted_project = {
            "id": project.get("id"),
            "name": project.get("name"),
            "description": project.get("description"),
            "status": project.get("status"),
            "plan": project.get("plan"),
            "website": project.get("website_url"),
            "socials": project.get("social_links"),
            "contract_subscription_date": project.get("contract_subscription_date"),
            "tickets_count": len(tickets),
            "tickets": tickets,
            "created_at": project.get("created_at"),
            "updated_at": project.get("updated_at")
        }
        
        return {
            "project": formatted_project,
            "client_id": client_id,
            "requested_by": current_user.get("username")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching project: {str(e)}")    


@app.get("/client/tickets/{ticket_id}")
async def client_get_ticket_details(
    ticket_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get detailed ticket information with tasks for the current client"""
    user_role = current_user.get("role")
    if user_role != "client":
        raise HTTPException(status_code=403, detail="Only clients can access this endpoint")
    
    client_id = current_user.get("id")
    
    # Get ticket with tasks
    ticket = await get_client_ticket_with_tasks(client_id, ticket_id)
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found or access denied")
    
    # Format response
    project_info = ticket.get("projects") or {}
    formatted_ticket = {
        "id": ticket.get("id"),
        "message": ticket.get("message"),
        "status": ticket.get("status"),
        "project": {
            "id": project_info.get("id"),
            "name": project_info.get("name"),
            "status": project_info.get("status")
        },
        "tasks": ticket.get("tasks", []),
        "tasks_summary": {
            "total": ticket.get("tasks_count", 0),
            "active": ticket.get("active_tasks", 0),
            "completed": ticket.get("completed_tasks", 0)
        },
        "created_at": ticket.get("created_at"),
        "updated_at": ticket.get("updated_at")
    }
    
    return {
        "ticket": formatted_ticket,
        "client_id": client_id,
        "requested_by": current_user.get("username")
    }


@app.get("/client/projects/{project_id}/tickets/{ticket_id}/tasks")
async def client_get_ticket_tasks(
    project_id: str,
    ticket_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get all tasks for a specific ticket in a project (client only)"""
    user_role = current_user.get("role")
    if user_role != "client":
        raise HTTPException(status_code=403, detail="Only clients can access this endpoint")
    
    client_id = current_user.get("id")
    
    try:
        admin_client = get_supabase_admin_client()
        
        # Verify project and ticket ownership
        ticket_check = admin_client.from_("tickets").select("""
            id,
            project_id,
            client_id,
            message,
            status
        """).eq("id", ticket_id).eq("project_id", project_id).eq("client_id", client_id).single().execute()
        
        if not ticket_check.data:
            raise HTTPException(status_code=404, detail="Ticket not found or access denied")
        
        ticket_info = ticket_check.data
        
        # Get tasks for this ticket
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
        """).eq("ticket_id", ticket_id).order("created_at", desc=True).execute()
        
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
        
        # Calculate statistics
        total_tasks = len(formatted_tasks)
        completed_tasks = len([t for t in formatted_tasks if t["status"] == "completed"])
        active_tasks = len([t for t in formatted_tasks if t["status"] == "in_progress"])
        
        return {
            "ticket": {
                "id": ticket_info.get("id"),
                "message": ticket_info.get("message"),
                "status": ticket_info.get("status")
            },
            "project_id": project_id,
            "tasks": formatted_tasks,
            "tasks_summary": {
                "total": total_tasks,
                "active": active_tasks,
                "completed": completed_tasks,
                "progress_percentage": round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0
            },
            "client_id": client_id,
            "requested_by": current_user.get("username")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tasks: {str(e)}")


# TIME TRACKING API
@app.post("/tasks/{task_id}/timer/start")
async def start_task_timer_endpoint(
    task_id: str,
    timer_data: dict,
    current_user: Dict = Depends(get_current_user)
):
    """Start timer for a task (assigned user or admin)"""
    try:
        user_id = current_user.get("id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        result = await start_task_timer(task_id, user_id)
        
        if "error" in result:
            if result["error"] == "Permission denied":
                raise HTTPException(status_code=403, detail=result["error"])
            elif result["error"] == "Task not found":
                raise HTTPException(status_code=404, detail=result["error"])
            elif "already running" in result["error"]:
                raise HTTPException(status_code=400, detail=result["error"])
            else:
                raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "message": "Timer started successfully",
            "task_id": task_id,
            "session": result.get("session"),
            "started_by": current_user.get("username")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting timer: {str(e)}")

@app.post("/tasks/{task_id}/timer/stop")
async def stop_task_timer_endpoint(
    task_id: str,
    timer_data: dict,
    current_user: Dict = Depends(get_current_user)
):
    """Stop timer for a task (assigned user or admin)"""
    try:
        user_id = current_user.get("id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        result = await stop_task_timer(task_id, user_id)
        
        if "error" in result:
            if result["error"] == "Permission denied":
                raise HTTPException(status_code=403, detail=result["error"])
            elif result["error"] == "Task not found":
                raise HTTPException(status_code=404, detail=result["error"])
            elif "No active timer" in result["error"]:
                raise HTTPException(status_code=400, detail=result["error"])
            else:
                raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "message": "Timer stopped successfully",
            "task_id": task_id,
            "session": result.get("session"),
            "total_time_minutes": result.get("total_time_minutes"),
            "sessions_count": result.get("sessions_count"),
            "stopped_by": current_user.get("username")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping timer: {str(e)}")

@app.get("/tasks/{task_id}/time-logs")
async def get_task_time_logs_endpoint(
    task_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get time logs for a task (assigned user, staff, or admin)"""
    try:
        user_id = current_user.get("id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        result = await get_task_time_logs(task_id, user_id)
        
        if "error" in result:
            if result["error"] == "Permission denied":
                raise HTTPException(status_code=403, detail=result["error"])
            elif result["error"] == "Task not found":
                raise HTTPException(status_code=404, detail=result["error"])
            else:
                raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "task": result,
            "requested_by": current_user.get("username")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching time logs: {str(e)}")

@app.get("/tasks/my/time-summary")
async def get_my_time_summary(current_user: Dict = Depends(get_current_user)):
    """Get time tracking summary for current user's tasks"""
    try:
        user_id = current_user.get("id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        admin_client = get_supabase_admin_client()
        
        # Get all tasks assigned to user with time data
        tasks_response = admin_client.from_("tasks").select("""
            id,
            action,
            status,
            priority,
            time_logs,
            total_time_minutes,
            time_sessions_count,
            created_at,
            tickets:ticket_id (
                id,
                message,
                projects:project_id (
                    id,
                    name
                )
            )
        """).eq("assigned_to", user_id).order("created_at", desc=True).execute()
        
        tasks = tasks_response.data if tasks_response.data else []
        
        # Calculate summary statistics
        total_time_minutes = sum(task.get("total_time_minutes", 0) for task in tasks)
        total_sessions = sum(task.get("time_sessions_count", 0) for task in tasks)
        active_timers = sum(1 for task in tasks if any(not log.get("end_time") for log in task.get("time_logs", [])))
        
        # Format tasks
        formatted_tasks = []
        for task in tasks:
            ticket_info = task.get("tickets") or {}
            project_info = ticket_info.get("projects") or {} if ticket_info else {}
            
            # Check for active timer
            time_logs = task.get("time_logs") or []
            active_session = next((log for log in time_logs if not log.get("end_time")), None)
            
            formatted_task = {
                "id": task.get("id"),
                "action": task.get("action"),
                "status": task.get("status"),
                "priority": task.get("priority"),
                "project_name": project_info.get("name") or "Unknown Project",
                "ticket_message": ticket_info.get("message") or "No ticket info",
                "time_summary": {
                    "total_minutes": task.get("total_time_minutes", 0),
                    "total_hours": round(task.get("total_time_minutes", 0) / 60, 2),
                    "sessions_count": task.get("time_sessions_count", 0),
                    "is_timer_running": active_session is not None,
                    "current_session_start": active_session.get("start_time") if active_session else None
                },
                "created_at": task.get("created_at")
            }
            formatted_tasks.append(formatted_task)
        
        return {
            "summary": {
                "total_time_minutes": total_time_minutes,
                "total_time_hours": round(total_time_minutes / 60, 2),
                "total_sessions": total_sessions,
                "active_timers": active_timers,
                "tasks_count": len(tasks)
            },
            "tasks": formatted_tasks,
            "user_id": user_id,
            "requested_by": current_user.get("username")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching time summary: {str(e)}")

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
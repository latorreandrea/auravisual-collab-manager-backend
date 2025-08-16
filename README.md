# Auravisual Collab Manager - Backend API

![Version](https://img.shields.io/badge/version-1.2.0-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green) ![Python](https://img.shields.io/badge/python-3.11+-blue)

Auravisual Collab Manager is a lightweight, full-stack project management platform built with **FastAPI**, **Supabase**, and **Flutter**. It is designed to help small teams effectively manage projects, tasks, deadlines, and multi-user collaboration.

## 🚀 Key Features

- 🔐 **JWT Authentication** with Supabase Auth integration
- 👥 **Role-based Access Control** (Admin, Internal Staff, Client)
- 🛡️ **Row Level Security** (RLS) for data protection
- 📊 **RESTful API** with comprehensive endpoints
- 🏗️ **Project Management** with full CRUD operations
- 📋 **Task Management** with status tracking and assignment
- 🎫 **Ticket System** for client communication
- 🐳 **Docker-ready** for easy deployment
- 🌐 **CORS Configuration** for cross-origin requests
- 📱 **Cross-platform** frontend support (Flutter)
- ⚡ **High Performance** with FastAPI and Uvicorn
- 🔧 **Environment-based** configuration

This project is part of my portfolio and demonstrates my experience with full-stack architecture, backend API design, secure authentication, and modern app development.

**This repository contains only the files to handle the BACKEND. Here https://github.com/latorreandrea/auravisual-collab-manager-mobile you will find the files for the frontend**

## 🏗️ Technical Architecture

### Backend Stack
- **FastAPI** - Modern, fast web framework for building APIs
- **Supabase** - PostgreSQL database with built-in authentication
- **PyJWT** - JSON Web Token implementation for secure authentication
- **Uvicorn** - Lightning-fast ASGI server
- **Python-dotenv** - Environment variables management

### Security Features
- **JWT Authentication** - Stateless token-based authentication
- **Role-Based Access Control** - Granular permission system
- **Row Level Security** - Database-level data protection
- **Environment Variables** - Secure credential management
- **CORS Protection** - Cross-origin request control
- **Input Validation** - Request data sanitization

---

## � Quick Start

### Prerequisites
- Python 3.11+
- Supabase account and project
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/latorreandrea/auravisual-collab-manager-backend.git
cd auravisual-collab-manager-backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment Configuration**
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your Supabase credentials
ENVIRONMENT=development
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_role_key
SECRET_KEY=your_jwt_secret_key
```

5. **Run the application**
```bash
# Development mode
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Deployment
```bash
# Build the image
docker build -t auravisual-backend .

# Run the container
docker run -p 8000:8000 --env-file .env auravisual-backend
```

---

## 📋 API Documentation

### Base URL
- **Production**: `https://app.auravisual.dk`
- **Development**: `http://localhost:8000`

### Authentication
All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## 🌐 Public Endpoints

### `GET /`
**Description:** API information and status  
**Authentication:** None required

```bash
curl https://app.auravisual.dk/
```

**Response:**
```json
{
  "message": "Auravisual Collab Manager API",
  "version": "1.0.0",
  "status": "running",
  "environment": "production"
}
```

### `GET /health`
**Description:** Service health check  
**Authentication:** None required

```bash
curl https://app.auravisual.dk/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "auravisual-backend"
}
```

### `GET /health/db`
**Description:** Database connectivity check  
**Authentication:** None required

```bash
curl https://app.auravisual.dk/health/db
```

**Response:**
```json
{
  "status": "connected",
  "database": "connected"
}
```

---

## 🔐 Authentication Endpoints

### `POST /auth/login`
**Description:** User authentication with email and password  
**Authentication:** None required

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "your_password"
}
```

**Example:**
```bash
curl -X POST https://app.auravisual.dk/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your_password"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid-here",
    "email": "user@example.com",
    "username": "username",
    "role": "client",
    "full_name": "User Name"
  }
}
```

### `GET /auth/me`
**Description:** Get current user information  
**Authentication:** Required  
**Roles:** All authenticated users

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  https://app.auravisual.dk/auth/me
```

**Response:**
```json
{
  "user": {
    "id": "uuid-here",
    "email": "user@example.com",
    "username": "username",
    "role": "client",
    "full_name": "User Name",
    "is_active": true
  },
  "authenticated": true
}
```

### `POST /auth/logout`
**Description:** User logout  
**Authentication:** Required  
**Roles:** All authenticated users

```bash
curl -X POST -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  https://app.auravisual.dk/auth/logout
```

**Response:**
```json
{
  "message": "Logged out successfully"
}
```

---

## 👑 Admin Endpoints

### `POST /auth/register`
**Description:** Register a new user  
**Authentication:** Required  
**Roles:** Admin only

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "password": "SecurePass123!",
  "full_name": "New User Name",
  "role": "client"
}
```

**Available Roles:** `admin`, `internal_staff`, `client`

**Example:**
```bash
curl -X POST https://app.auravisual.dk/auth/register \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePass123!",
    "full_name": "New User Name",
    "role": "client"
  }'
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user_id": "new-uuid-here",
  "email": "newuser@example.com",
  "role": "client",
  "created_by": "admin_username"
}
```

### `GET /admin/users`
**Description:** List all users in the system  
**Authentication:** Required  
**Roles:** Admin only

```bash
curl -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
  https://app.auravisual.dk/admin/users
```

**Response:**
```json
{
  "total_users": 5,
  "users": [
    {
      "id": "uuid-1",
      "email": "admin@auravisual.dk",
      "username": "admin_user",
      "full_name": "Admin User",
      "role": "admin",
      "is_active": true,
      "created_at": "2025-01-01T10:00:00Z"
    }
  ],
  "requested_by": "admin_username"
}
```

### `GET /admin/users/staff`
**Description:** List all internal staff members  
**Authentication:** Required  
**Roles:** Admin only

```bash
curl -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
  https://app.auravisual.dk/admin/users/staff
```

**Response:**
```json
{
  "total_staff": 2,
  "staff": [
    {
      "id": "uuid-2",
      "email": "staff@auravisual.dk",
      "username": "staff_user",
      "full_name": "Staff Member",
      "role": "internal_staff",
      "is_active": true,
      "created_at": "2025-01-01T11:00:00Z"
    }
  ],
  "requested_by": "admin_username"
}
```

### `GET /admin/users/clients`
**Description:** List all client users  
**Authentication:** Required  
**Roles:** Admin, Internal Staff

```bash
curl -H "Authorization: Bearer ADMIN_OR_STAFF_JWT_TOKEN" \
  https://app.auravisual.dk/admin/users/clients
```

**Response:**
```json
{
  "total_clients": 10,
  "clients": [
    {
      "id": "uuid-3",
      "email": "client@example.com",
      "username": "client_user",
      "full_name": "Client Name",
      "role": "client",
      "is_active": true,
      "created_at": "2025-01-01T12:00:00Z"
    }
  ],
  "requested_by": "admin_or_staff_username"
}
```

---

## 🐛 Debug Endpoints (Development Only)

### `GET /debug/config`
**Description:** Debug configuration information  
**Authentication:** Required  
**Roles:** Admin only  
**Environment:** Development only

```bash
curl -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
  http://localhost:8000/debug/config
```

**Response:**
```json
{
  "environment": "development",
  "debug": true,
  "cors_origins": ["http://localhost:3000"],
  "api_docs_enabled": true,
  "supabase_configured": true,
  "accessed_by": "admin_username"
}
```

### `GET /debug/db`
**Description:** Debug database connection details  
**Authentication:** Required  
**Roles:** Admin only  
**Environment:** Development only

```bash
curl -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
  http://localhost:8000/debug/db
```

---

## 👥 User Roles & Permissions

### Role Hierarchy
- **Admin** (`admin`)
  - Full system access
  - User management
  - All endpoints access
  - Debug endpoints (development)

- **Internal Staff** (`internal_staff`)
  - View client users
  - Limited admin functions
  - Cannot manage other staff or admins

- **Client** (`client`)
  - Own profile access only
  - Project/task access (when implemented)
  - Limited system access

### Permission Matrix

| Endpoint | Admin | Internal Staff | Client |
|----------|-------|----------------|--------|
| `GET /` | ✅ | ✅ | ✅ |
| `GET /health*` | ✅ | ✅ | ✅ |
| `POST /auth/login` | ✅ | ✅ | ✅ |
| `GET /auth/me` | ✅ | ✅ | ✅ |
| `POST /auth/logout` | ✅ | ✅ | ✅ |
| `POST /auth/register` | ✅ | ❌ | ❌ |
| `GET /admin/users` | ✅ | ❌ | ❌ |
| `GET /admin/users/staff` | ✅ | ❌ | ❌ |
| `GET /admin/users/clients` | ✅ | ✅ | ❌ |
| `GET /debug/*` | ✅ (dev only) | ❌ | ❌ |

---

## 🔧 Environment Configuration

### Required Environment Variables

Create a `.env` file in the project root:

```bash
# Application Environment
ENVIRONMENT=development  # or 'production'

# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_anon_public_key
SUPABASE_SERVICE_KEY=your_service_role_key

# JWT Configuration
SECRET_KEY=your_super_secret_jwt_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration (production only)
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

### Environment-Specific Features

**Development (`ENVIRONMENT=development`):**
- API documentation available at `/docs`
- ReDoc documentation at `/redoc`
- Debug endpoints enabled
- Detailed error responses
- CORS allows localhost origins

**Production (`ENVIRONMENT=production`):**
- API documentation disabled
- Debug endpoints disabled
- CORS restricted to specified origins
- Enhanced security headers

---

## 🐳 Docker Support

### Build and Run with Docker

```bash
# Build the Docker image
docker build -t auravisual-backend .

# Run with environment variables
docker run -p 8000:8000 \
  -e SUPABASE_URL=your_url \
  -e SUPABASE_KEY=your_key \
  -e SECRET_KEY=your_secret \
  auravisual-backend
```

### Docker Compose (Optional)

```yaml
version: '3.8'
services:
  auravisual-backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
      - SECRET_KEY=${SECRET_KEY}
```

---

## 🌐 Production Deployment

### Google Cloud Run (Current Setup)

The application is currently deployed on Google Cloud Run:
- **URL**: https://app.auravisual.dk
- **SSL**: Automatic HTTPS with custom domain
- **Scaling**: 0-10 instances based on demand
- **Environment**: Production configuration

### Deployment Steps
1. Set environment variables in Cloud Run
2. Configure custom domain (optional)
3. Set up CI/CD pipeline (recommended)
4. Monitor logs and metrics

---

## 📊 API Response Formats

### Success Response Format
```json
{
  "message": "Operation successful",
  "data": { /* response data */ },
  "status": "success"
}
```

### Error Response Format
```json
{
  "detail": "Error description",
  "status": "error",
  "status_code": 400
}
```

### Authentication Error
```json
{
  "detail": "Could not validate credentials",
  "status_code": 401
}
```

### Authorization Error
```json
{
  "detail": "Not enough permissions",
  "status_code": 403
}
```

---

## 🧪 Testing the API

### Using curl

```bash
# 1. Test public endpoints
curl https://app.auravisual.dk/health

# 2. Login and get token
TOKEN=$(curl -s -X POST https://app.auravisual.dk/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"your@email.com","password":"yourpass"}' \
  | jq -r '.access_token')

# 3. Use the token for protected endpoints
curl -H "Authorization: Bearer $TOKEN" \
  https://app.auravisual.dk/auth/me
```

### Using Python Requests

```python
import requests

# Login
login_response = requests.post(
    "https://app.auravisual.dk/auth/login",
    json={"email": "your@email.com", "password": "yourpass"}
)
token = login_response.json()["access_token"]

# Make authenticated request
headers = {"Authorization": f"Bearer {token}"}
user_response = requests.get(
    "https://app.auravisual.dk/auth/me",
    headers=headers
)
print(user_response.json())
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Andrea Latorre**
- GitHub: [@latorreandrea](https://github.com/latorreandrea)
- Frontend Repository: [auravisual-collab-manager-mobile](https://github.com/latorreandrea/auravisual-collab-manager-mobile)

---

## 🔮 Roadmap

- [ ] Project management endpoints
- [ ] Task management system  
- [ ] File upload functionality
- [ ] Real-time notifications
- [ ] Advanced filtering and search
- [ ] API rate limiting
- [ ] Comprehensive test suite
- [ ] CI/CD pipeline

---

## 🧩 Projects, Tickets & Tasks - Additional API Details

This section documents the project/ticket/task endpoints that support the core collaboration flow. All endpoints below require a valid Bearer token (Supabase session token). Admin-only endpoints require the caller to have the `admin` role.

### Ticket statuses
- `to_read` - New ticket, not yet reviewed by staff/admin
- `processing` - Ticket currently being processed (tasks have been created)
- `accepted` - Ticket request accepted / approved
- `rejected` - Ticket request rejected

### Task statuses
- `in_progress` - Task is active and work is ongoing
- `completed` - Task has been finished

> Note: Active tasks are those with `status = in_progress`.

---

### GET /admin/projects
Description: Admin endpoint that returns all projects with their client information and only the open tickets and active tasks for each project.
Authentication: Bearer token (admin)

Response shape (trimmed):

```json
{
  "total_projects": 3,
  "projects": [
    {
      "id": "uuid-project-1",
      "name": "Website Redesign",
      "status": "in_development",
      "plan": "Aura Boost",
      "client": { "id": "uuid-client-1", "email": "client@example.com", "username": "client1" },
      "open_tickets_count": 2,
      "open_tasks_count": 5,
      "open_tickets": [
        {
          "id": "uuid-ticket-1",
          "message": "Change header color",
          "status": "to_read",
          "active_tasks_count": 2,
          "active_tasks": [ { "id": "uuid-task-1", "action": "Change CSS header color", "assigned_to": "uuid-staff-1", "status": "in_progress" } ]
        }
      ],
      "created_at": "2025-01-01T10:00:00Z"
    }
  ]
}
```

Example curl:

```bash
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  https://app.auravisual.dk/admin/projects
```

---

### GET /admin/projects/{project_id}
Description: Admin endpoint that returns a single project with client info, open tickets and their active tasks.
Authentication: Bearer token (admin)

Response shape: same as a single project object from the list above.

Example curl:

```bash
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  https://app.auravisual.dk/admin/projects/PROJECT_UUID
```

---

### POST /admin/projects
Description: Admin endpoint to create a new project. Requires project name and client_id. Website and socials fields are optional.
Authentication: Bearer token (admin)

Request body:

```json
{
  "name": "New Website Project",
  "client_id": "uuid-client-1",
  "website": "https://example.com",    // optional
  "socials": "instagram: @example"     // optional
}
```

Response:

```json
{
  "message": "Project created successfully",
  "project": {
    "id": "uuid-project-new",
    "name": "New Website Project",
    "client_id": "uuid-client-1",
    "website": "https://example.com",
    "socials": "instagram: @example",
    "status": "active",
    "created_at": "2025-08-16T10:00:00Z"
  },
  "created_by": "admin_username"
}
```

Example curl:

```bash
curl -X POST https://app.auravisual.dk/admin/projects \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"My New Project","client_id":"CLIENT_UUID","website":"https://example.com"}'
```

---

### POST /admin/tasks
Description: Admin creates a single task.
Authentication: Bearer token (admin)

Request body:

```json
{
  "ticket_id": "uuid-ticket-1",
  "assigned_to": "uuid-staff-1",
  "action": "Implement responsive nav",
  "priority": "high"   // optional: one of low, medium, high, urgent
}
```

Response: created task object (includes `status` defaulting to `in_progress`).

Example curl:

```bash
curl -X POST https://app.auravisual.dk/admin/tasks \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"ticket_id":"TICKET_UUID","assigned_to":"STAFF_UUID","action":"Fix layout","priority":"high"}'
```

---

### POST /admin/tickets/{ticket_id}/tasks (bulk create)
Description: Admin creates multiple tasks for a ticket in a single request. Each task must include `action` and `assigned_to`. `priority` is optional. After tasks are created the ticket's status is updated to `processing`.
Authentication: Bearer token (admin)

Request body:

```json
{
  "tasks": [
    {"action":"Change header color to brand green","assigned_to":"uuid-staff-1","priority":"high"},
    {"action":"Compress hero images","assigned_to":"uuid-staff-2"}
  ]
}
```

Response (trimmed):

```json
{
  "message": "Tasks created and ticket moved to 'processing'",
  "created_tasks_count": 2,
  "created_tasks": [ {"id": "uuid-task-1", "action": "..."}, {"id": "uuid-task-2"} ],
  "ticket_id": "uuid-ticket-1",
  "ticket_status": "processing"
}
```

Example curl:

```bash
curl -X POST https://app.auravisual.dk/admin/tickets/TICKET_UUID/tasks \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tasks":[{"action":"Fix bug","assigned_to":"STAFF_UUID"}]}'
```

---

### GET /tasks/my
Description: Get tasks assigned to the current authenticated user. Optional query param `status` filters by `in_progress` or `completed`.
Authentication: Bearer token (any authenticated user)

Example:

```bash
curl -H "Authorization: Bearer $USER_TOKEN" \
  "https://app.auravisual.dk/tasks/my?status=in_progress"
```

### GET /tasks/my/active
Description: Convenience endpoint that returns only active tasks (`status = in_progress`) for the current user.

Example:

```bash
curl -H "Authorization: Bearer $USER_TOKEN" \
  https://app.auravisual.dk/tasks/my/active
```

### PATCH /tasks/{task_id}/status
Description: Update the status of a task. Only the assigned user or an admin may update a task's status. Allowed values: `in_progress`, `completed`.
Authentication: Bearer token (assigned user or admin)

Request body:

```json
{"status":"completed"}
```

Example curl:

```bash
curl -X PATCH https://app.auravisual.dk/tasks/TASK_UUID/status \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":"completed"}'
```

---

## ✅ Summary of permissions (quick reference)

| Resource | Admin | Internal Staff | Client |
|---|---:|:---:|:---:|
| Create project | ✅ | ❌ | ❌ |
| Read projects | ✅ | ✅ | ✅ (own only) |
| Create ticket | ❌ | ❌ | ✅ (own projects) |
| Read ticket (own) | ✅ | ✅ | ✅ |
| Create tasks | ✅ | ❌ | ❌ |
| Read assigned tasks | ✅ | ✅ | ✅ (own only) |
| Update task status | ✅ | ✅ (if assigned) | ❌ |

---

## 🔄 Recent Updates

### Version 1.2.0 (August 2025)
- ✅ **NEW: Project Creation Endpoint** - Admin users can now create new projects via `POST /admin/projects`
- ✅ **Enhanced Project Management** - Added comprehensive project creation with validation
- ✅ **Optional Fields Support** - Website and social media fields are now optional in project creation
- ✅ **Improved Error Handling** - Better error messages for project creation validation
- ✅ **Updated Documentation** - Complete API documentation with examples for all endpoints

### Features Added:
- `POST /admin/projects` - Create new projects with required name and client_id
- Client validation - Ensures the specified client_id exists and has "client" role
- Flexible project data - Website and socials fields are optional
- Consistent response format - Follows established API response patterns

---


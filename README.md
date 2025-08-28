# Auravisual Collab Manager - Backend API

![Version](https://img.shields.io/badge/version-2.1.0-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green) ![Python](https://img.shields.io/badge/python-3.11+-blue)

Auravisual Collab Manager is a comprehensive, full-stack project management platform built with **FastAPI**, **Supabase**, and **Flutter**. It is designed to help agencies and teams effectively manage client projects, tasks, communication, and collaboration workflows.

## 🚀 Key Features

- 🔐 **JWT Authentication** with Supabase Auth integration
- 👥 **Role-based Access Control** (Admin, Internal Staff, Client)
- 🛡️ **Row Level Security** (RLS) for data protection
- 📊 **RESTful API** with comprehensive endpoints
- 🏗️ **Complete Project Management** with client assignment and tracking
- 📋 **Advanced Task Management** with status tracking, priority levels, and assignment
- 🕒 **Time Tracking System** with start/stop timers and detailed session logs
- 🎫 **Client Ticket System** for seamless client-team communication
- 📈 **Admin Dashboard** with real-time statistics and insights
- 👤 **Client Portal** with project visibility and task progress monitoring
- 🔄 **Multi-role Workflows** for admin, staff, and client interactions
- 💰 **Time-based Billing Support** with accurate work duration tracking
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

## � Management Workflows

### 👨‍💼 Admin Workflow
**Complete system management and oversight**

1. **User Management**
   - Create clients via `POST /auth/register`
   - Create internal staff accounts
   - View all users and their statistics
   - Access dashboard with system metrics

2. **Project Management**
   - Create projects for clients via `POST /admin/projects`
   - View all projects with client relations and status
   - Monitor project progress and ticket activity
   - Access comprehensive project analytics

3. **Task & Ticket Management**
   - View all tickets from clients (status: `to_read`)
   - Create individual tasks via `POST /admin/tasks`
   - Create bulk tasks for tickets via `POST /admin/tickets/{id}/tasks`
   - When tasks are created, ticket status automatically changes to `accepted`
   - Monitor task assignments and completion rates
   - Reject tickets if needed (status: `rejected`)

4. **Dashboard & Analytics**
   - Access real-time statistics via `GET /admin/dashboard`
   - Monitor active projects, open tickets, and task progress
   - Track client and staff performance metrics

### 👨‍💻 Internal Staff Workflow
**Task execution and project development**

1. **Task Management**
   - View assigned tasks via `GET /tasks/my`
   - Focus on active tasks via `GET /tasks/my/active`
   - Update task status as work progresses via `PATCH /tasks/{id}/status`
   - Track personal task statistics and workload

2. **Project Visibility**
   - View all projects they're involved in
   - Access project details and client information
   - Monitor ticket requirements and client feedback

3. **Collaboration**
   - Work with task priorities (low, medium, high, urgent)
   - Coordinate with team members on project delivery
   - Update task completion status for client transparency

### 👤 Client Workflow
**Project monitoring and communication**

1. **Project Visibility**
   - View all their projects via `GET /client/projects`
   - Access detailed project information via `GET /client/projects/{id}`
   - Monitor project status and progress
   - Track project timeline and milestones

2. **Communication via Tickets**
   - Create tickets for project requests via `POST /client/projects/{id}/tickets`
   - New tickets start with status `to_read`
   - Submit feedback, change requests, and bug reports
   - View all their tickets across projects via `GET /client/tickets`
   - Filter tickets by specific projects
   - Monitor ticket status: `to_read` → `accepted` (when admin creates tasks) or `rejected`

3. **Progress Monitoring**
   - View detailed ticket information via `GET /client/tickets/{id}`
   - Monitor task progress for each ticket
   - See which team members are working on their requests
   - Track task completion status and priority levels
   - Access task details via `GET /client/projects/{id}/tickets/{id}/tasks`

4. **Real-time Work Visibility**
   - View active timers for their projects via `GET /client/active-timers`
   - See who is currently working on their tasks
   - Monitor real-time work progress and team allocation
   - Get transparency into current development activities

---

## 🎯 Typical Project Lifecycle

### Phase 1: Project Setup (Admin)
```bash
# 1. Admin creates client account
POST /auth/register
{
  "email": "client@company.com",
  "password": "SecurePass123",
  "full_name": "Client Company Ltd",
  "role": "client"
}

# 2. Admin creates project for client
POST /admin/projects
{
  "name": "Company Website Redesign",
  "client_id": "client-uuid",
  "website": "https://company.com",
  "socials": "instagram: @company"
}
```

### Phase 2: Client Communication
```bash
# Client creates tickets for requirements
POST /client/projects/{project_id}/tickets
{
  "message": "I need the header color changed to match our brand colors"
}
```

### Phase 3: Task Management (Admin)
```bash
# Admin creates tasks for the ticket
POST /admin/tickets/{ticket_id}/tasks
{
  "tasks": [
    {
      "action": "Update header CSS with new brand colors",
      "assigned_to": "staff-uuid",
      "priority": "high"
    },
    {
      "action": "Test color changes across all pages",
      "assigned_to": "tester-uuid", 
      "priority": "medium"
    }
  ]
}
# Ticket status automatically changes from "to_read" to "accepted"
```

### Phase 4: Development (Staff)
```bash
# Staff updates task status as work progresses
PATCH /tasks/{task_id}/status
{
  "status": "completed"
}
```

### Phase 5: Client Monitoring
```bash
```

### Phase 5: Client Monitoring
```bash
# Client monitors progress
GET /client/tickets/{ticket_id}
# Shows tasks, assigned staff, and completion status
```

---

## ⏱️ Time Tracking System

The Auravisual time tracking system enables accurate monitoring of time worked on each task, providing billing, reporting, and workload management capabilities.

### 🔧 Architecture

Time tracking uses a **flexible JSONB approach**:
- `time_logs` field in the `tasks` table to store work sessions
- Automatic calculation of total time and session count
- Support for multiple sessions per task
- Precise start/stop tracking with timestamps

### 👨‍💼 Staff Workflow

#### 1. **Start Timer**
```bash
# Staff starts working on a task
POST /tasks/{task_id}/timer/start
Authorization: Bearer <staff_token>
```

**Internal Process:**
- System verifies permissions (`admin` or `internal_staff`)
- Checks that user doesn't already have an active timer
- Creates new session with start timestamp
- Updates task status to "in progress" if necessary

#### 2. **Stop Timer**
```bash
# Staff completes work session
POST /tasks/{task_id}/timer/stop
Authorization: Bearer <staff_token>
```

**Internal Process:**
- Finds user's active session for that task
- Calculates session duration in minutes
- Updates totals: `total_time_minutes` and `time_sessions_count`
- Closes session with end timestamp

#### 3. **Time Monitoring**
```bash
# Staff views their worked time
GET /tasks/my/time-summary
Authorization: Bearer <staff_token>
```

### 👑 Admin Workflow

#### 1. **Team Monitoring**
```bash
# Admin views all tasks with tracked time
GET /admin/tasks
Authorization: Bearer <admin_token>
```

#### 2. **Specific Details**
```bash
# Admin examines sessions for a specific task
GET /tasks/{task_id}/time-logs
Authorization: Bearer <admin_token>
```

#### 3. **Timer Management**
Admins can:
- Start/stop timers for any task
- View sessions from all staff members
- Access aggregated data for reporting and billing

### 👤 Client Visibility

Clients have limited but informative access:
- See `total_time_minutes` and `time_sessions_count` through tickets
- No access to individual session details
- Can monitor progress based on time invested

### 📊 Data Structure

#### Task Record with Time Tracking
```json
{
  "id": "task-uuid",
  "title": "Implement user authentication",
  "status": "in_progress",
  "total_time_minutes": 145,
  "time_sessions_count": 3,
  "time_logs": [
    {
      "session_id": "session-1",
      "user_id": "staff-uuid",
      "start_time": "2024-01-15T09:00:00Z",
      "end_time": "2024-01-15T10:30:00Z",
      "duration_minutes": 90
    },
    {
      "session_id": "session-2", 
      "user_id": "staff-uuid",
      "start_time": "2024-01-15T14:00:00Z",
      "end_time": "2024-01-15T14:55:00Z",
      "duration_minutes": 55
    },
    {
      "session_id": "session-3",
      "user_id": "staff-uuid", 
      "start_time": "2024-01-15T16:00:00Z",
      "end_time": null,
      "duration_minutes": null
    }
  ]
}
```

### 🚫 Controls and Validations

1. **Active Sessions**: A user can only have one active session at a time
2. **Permissions**: Only `admin` and `internal_staff` can manage timers
3. **Task Assignment**: User must be assigned to task to track time
4. **Data Integrity**: Automatic control of orphaned sessions and cleanup

### 💡 Advanced Use Cases

#### Daily Reporting
```bash
# Staff views their time summary
GET /tasks/my/time-summary?date=2024-01-15
```

#### Billing and Invoicing
- `total_time_minutes` field usable for billing calculations
- Granular tracking for hourly rates
- Detailed reporting for client projects

#### Project Management
- Estimate vs. actual time for tasks
- Identification of time-consuming tasks
- Team resource allocation optimization

---

## 📋 API Documentation
```

---

## �📋 API Documentation

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
- `accepted` - Ticket request accepted and tasks have been created
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

### GET /admin/dashboard
Description: Admin endpoint that returns comprehensive system statistics including active projects, clients, open tickets, and active tasks.
Authentication: Bearer token (admin only)

Response:

```json
{
  "dashboard": {
    "projects": {
      "total": 15,
      "active": 8,
      "completed": 7
    },
    "clients": {
      "total": 12
    },
    "staff": {
      "total": 4
    },
    "tickets": {
      "open": 23
    },
    "tasks": {
      "active": 45
    }
  },
  "summary": {
    "total_active_projects": 8,
    "total_clients": 12,
    "open_tickets": 23,
    "active_tasks": 45,
    "total_staff": 4
  },
  "requested_by": "admin_username",
  "timestamp": "2025-08-17T16:00:00Z"
}
```

Example curl:

```bash
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  https://app.auravisual.dk/admin/dashboard
```

---

### GET /admin/users/clients
Description: List all clients with project counts and recent projects information.
Authentication: Bearer token (admin/staff)

Response:

```json
{
  "total_clients": 3,
  "clients": [
    {
      "id": "uuid-client-1",
      "email": "client@example.com",
      "username": "client1",
      "full_name": "Client Company",
      "role": "client",
      "is_active": true,
      "created_at": "2025-01-01T10:00:00Z",
      "projects_count": 2,
      "recent_projects": [
        {
          "id": "uuid-project-1",
          "name": "Website Redesign",
          "status": "in_development",
          "created_at": "2025-01-15T10:00:00Z"
        }
      ]
    }
  ],
  "requested_by": "admin_username"
}
```

Example curl:

```bash
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  https://app.auravisual.dk/admin/users/clients
```

---

## 👤 Client API Endpoints

### GET /client/projects
Description: List all projects for the current authenticated client with ticket statistics.
Authentication: Bearer token (client only)

Response:

```json
{
  "total_projects": 2,
  "projects": [
    {
      "id": "uuid-project-1",
      "name": "Website E-commerce",
      "description": "Complete e-commerce solution",
      "status": "in_development",
      "plan": "Aura Boost",
      "website": "https://example.com",
      "socials": "instagram: @example",
      "tickets_count": 3,
      "open_tickets_count": 1,
      "created_at": "2025-01-01T10:00:00Z"
    }
  ],
  "client_id": "uuid-client-1",
  "requested_by": "client_username"
}
```

Example curl:

```bash
curl -H "Authorization: Bearer $CLIENT_TOKEN" \
  https://app.auravisual.dk/client/projects
```

---

### POST /client/projects/{project_id}/tickets
Description: Create a new ticket for a specific project (client can only create tickets for their own projects).
Authentication: Bearer token (client only)

Request body:

```json
{
  "message": "I would like to change the header color to match our brand colors better"
}
```

Response:

```json
{
  "message": "Ticket created successfully",
  "ticket": {
    "id": "uuid-ticket-new",
    "project_id": "uuid-project-1",
    "client_id": "uuid-client-1",
    "message": "I would like to change the header color...",
    "status": "to_read",
    "created_at": "2025-08-17T16:30:00Z"
  },
  "project_id": "uuid-project-1",
  "created_by": "client_username"
}
```

Example curl:

```bash
curl -X POST https://app.auravisual.dk/client/projects/PROJECT_UUID/tickets \
  -H "Authorization: Bearer $CLIENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Please update the contact form validation"}'
```

---

### GET /client/tickets
Description: List all tickets for the current client with task details and progress information.
Authentication: Bearer token (client only)

Query Parameters:
- `project_id` (optional): Filter tickets by specific project

Response:

```json
{
  "total_tickets": 2,
  "tickets": [
    {
      "id": "uuid-ticket-1",
      "message": "Change header color to brand green",
      "status": "accepted",
      "project": {
        "id": "uuid-project-1",
        "name": "Website E-commerce",
        "status": "in_development"
      },
      "tasks": [
        {
          "id": "uuid-task-1",
          "action": "Update CSS header color",
          "priority": "medium",
          "status": "in_progress",
          "assigned_to": {
            "name": "Marco Developer",
            "username": "marco_dev"
          },
          "created_at": "2025-08-17T10:00:00Z"
        }
      ],
      "tasks_summary": {
        "total": 2,
        "active": 1,
        "completed": 1
      },
      "created_at": "2025-08-17T09:00:00Z"
    }
  ],
  "project_filter": null,
  "client_id": "uuid-client-1",
  "requested_by": "client_username"
}
```

Example curl:

```bash
# All tickets
curl -H "Authorization: Bearer $CLIENT_TOKEN" \
  https://app.auravisual.dk/client/tickets

# Tickets for specific project
curl -H "Authorization: Bearer $CLIENT_TOKEN" \
  "https://app.auravisual.dk/client/tickets?project_id=PROJECT_UUID"
```

---

### GET /client/tickets/{ticket_id}
Description: Get detailed information about a specific ticket including all associated tasks and their progress.
Authentication: Bearer token (client only)

Response:

```json
{
  "ticket": {
    "id": "uuid-ticket-1",
    "message": "Change header color to brand green",
    "status": "accepted",
    "project": {
      "id": "uuid-project-1",
      "name": "Website E-commerce",
      "status": "in_development"
    },
    "tasks": [
      {
        "id": "uuid-task-1",
        "action": "Update CSS header color from blue to green",
        "priority": "medium",
        "status": "in_progress",
        "assigned_to": {
          "name": "Marco Developer",
          "username": "marco_dev"
        },
        "created_at": "2025-08-17T10:00:00Z",
        "updated_at": "2025-08-17T10:30:00Z"
      }
    ],
    "tasks_summary": {
      "total": 2,
      "active": 1,
      "completed": 1
    },
    "created_at": "2025-08-17T09:00:00Z",
    "updated_at": "2025-08-17T10:00:00Z"
  },
  "client_id": "uuid-client-1",
  "requested_by": "client_username"
}
```

Example curl:

```bash
curl -H "Authorization: Bearer $CLIENT_TOKEN" \
  https://app.auravisual.dk/client/tickets/TICKET_UUID
```

---

### GET /client/projects/{project_id}/tickets/{ticket_id}/tasks
Description: Get all tasks for a specific ticket with detailed progress information and completion percentage.
Authentication: Bearer token (client only)

Response:

```json
{
  "ticket": {
    "id": "uuid-ticket-1",
    "message": "Change header color to brand green",
    "status": "accepted"
  },
  "project_id": "uuid-project-1",
  "tasks": [
    {
      "id": "uuid-task-1",
      "action": "Update CSS header color from blue to green",
      "priority": "medium",
      "status": "in_progress",
      "assigned_to": {
        "name": "Marco Developer",
        "username": "marco_dev"
      },
      "created_at": "2025-08-17T10:00:00Z",
      "updated_at": "2025-08-17T10:30:00Z"
    }
  ],
  "tasks_summary": {
    "total": 2,
    "active": 1,
    "completed": 1,
    "progress_percentage": 50.0
  },
  "client_id": "uuid-client-1",
  "requested_by": "client_username"
}
```

Example curl:

```bash
curl -H "Authorization: Bearer $CLIENT_TOKEN" \
  https://app.auravisual.dk/client/projects/PROJECT_UUID/tickets/TICKET_UUID/tasks
```

---

### GET /client/active-timers
**Description:** Get all active timers for tasks in client's projects  
**Authentication:** Bearer token (client only)

**Response:**
```json
{
  "message": "Active timers retrieved successfully",
  "client_id": "uuid-client-1",
  "active_timers": [
    {
      "task_id": "uuid-task-1",
      "task_action": "Update header CSS with new brand colors",
      "start_time": "2025-08-28T14:30:00Z",
      "session_id": "uuid-session-1",
      "user_id": "uuid-staff-1",
      "user_name": "John Developer",
      "user_username": "john.dev",
      "project": {
        "id": "uuid-project-1",
        "name": "Company Website Redesign"
      },
      "ticket": {
        "id": "uuid-ticket-1",
        "message": "Please update header colors to match brand"
      }
    },
    {
      "task_id": "uuid-task-2", 
      "task_action": "Test responsive design on mobile devices",
      "start_time": "2025-08-28T15:45:00Z",
      "session_id": "uuid-session-2",
      "user_id": "uuid-staff-2",
      "user_name": "Sarah Tester",
      "user_username": "sarah.test",
      "project": {
        "id": "uuid-project-1",
        "name": "Company Website Redesign"
      },
      "ticket": {
        "id": "uuid-ticket-2",
        "message": "Mobile layout needs optimization"
      }
    }
  ],
  "total_active_timers": 2,
  "projects_checked": 1,
  "timestamp": "2025-08-28T16:00:00Z",
  "requested_by": "client_username"
}
```

**Example curl:**
```bash
curl -H "Authorization: Bearer $CLIENT_TOKEN" \
  https://app.auravisual.dk/client/active-timers
```

**Use Cases:**
- **Real-time Work Monitoring**: Clients can see who is actively working on their projects
- **Transparency**: Clear visibility into current work progress and team allocation
- **Communication**: Helps clients know when team members are available for questions
- **Project Status**: Immediate insight into active development work

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
Description: Admin creates multiple tasks for a ticket in a single request. Each task must include `action` and `assigned_to`. `priority` is optional. After tasks are created the ticket's status is updated to `accepted`.
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
  "message": "Tasks created and ticket moved to 'accepted'",
  "created_tasks_count": 2,
  "created_tasks": [ {"id": "uuid-task-1", "action": "..."}, {"id": "uuid-task-2"} ],
  "ticket_id": "uuid-ticket-1",
  "ticket_status": "accepted"
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
| View active timers | ✅ | ✅ | ✅ (own projects) |

---

## ⏱️ Time Tracking API Endpoints

### POST /tasks/{task_id}/timer/start
**Description:** Start a timer for a specific task  
**Authentication:** Bearer token (admin or internal_staff)  
**Permission:** User must be assigned to the task

**Request:**
```bash
curl -X POST https://app.auravisual.dk/tasks/TASK_UUID/timer/start \
  -H "Authorization: Bearer $STAFF_TOKEN"
```

**Response:**
```json
{
  "message": "Timer started successfully",
  "task_id": "uuid-task-1",
  "session_id": "uuid-session-1",
  "start_time": "2024-01-15T09:00:00Z",
  "user_id": "uuid-staff-1"
}
```

**Error Cases:**
- `403` - User not assigned to task or insufficient permissions
- `400` - User already has an active timer for this task
- `404` - Task not found

---

### POST /tasks/{task_id}/timer/stop
**Description:** Stop an active timer for a specific task  
**Authentication:** Bearer token (admin or internal_staff)  
**Permission:** User must have an active session for this task

**Request:**
```bash
curl -X POST https://app.auravisual.dk/tasks/TASK_UUID/timer/stop \
  -H "Authorization: Bearer $STAFF_TOKEN"
```

**Response:**
```json
{
  "message": "Timer stopped successfully",
  "task_id": "uuid-task-1",
  "session_id": "uuid-session-1",
  "start_time": "2024-01-15T09:00:00Z",
  "end_time": "2024-01-15T10:30:00Z",
  "duration_minutes": 90,
  "total_time_minutes": 145,
  "time_sessions_count": 2
}
```

**Error Cases:**
- `404` - No active timer found for this user and task
- `403` - Insufficient permissions

---

### GET /tasks/{task_id}/time-logs
**Description:** Get detailed time logs for a specific task  
**Authentication:** Bearer token (admin or internal_staff)  
**Permission:** Admin can view all logs, staff can view only their own logs

**Request:**
```bash
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  https://app.auravisual.dk/tasks/TASK_UUID/time-logs
```

**Response:**
```json
{
  "task_id": "uuid-task-1",
  "task_title": "Implement user authentication",
  "total_time_minutes": 145,
  "time_sessions_count": 3,
  "time_logs": [
    {
      "session_id": "session-1",
      "user_id": "uuid-staff-1", 
      "user_name": "John Developer",
      "start_time": "2024-01-15T09:00:00Z",
      "end_time": "2024-01-15T10:30:00Z",
      "duration_minutes": 90
    },
    {
      "session_id": "session-2",
      "user_id": "uuid-staff-1",
      "user_name": "John Developer", 
      "start_time": "2024-01-15T14:00:00Z",
      "end_time": "2024-01-15T14:55:00Z",
      "duration_minutes": 55
    },
    {
      "session_id": "session-3",
      "user_id": "uuid-staff-1",
      "user_name": "John Developer",
      "start_time": "2024-01-15T16:00:00Z",
      "end_time": null,
      "duration_minutes": null,
      "status": "active"
    }
  ],
  "active_sessions": 1
}
```

---

### GET /tasks/my/time-summary
**Description:** Get time tracking summary for the current user  
**Authentication:** Bearer token (admin or internal_staff)  
**Optional Query Parameters:**
- `date` - Filter by specific date (YYYY-MM-DD)
- `project_id` - Filter by project
- `active_only` - Show only tasks with active timers

**Request:**
```bash
curl -H "Authorization: Bearer $STAFF_TOKEN" \
  "https://app.auravisual.dk/tasks/my/time-summary?date=2024-01-15"
```

**Response:**
```json
{
  "user_id": "uuid-staff-1",
  "user_name": "John Developer",
  "date": "2024-01-15",
  "total_time_today": 145,
  "active_timers": 1,
  "tasks": [
    {
      "task_id": "uuid-task-1",
      "task_title": "Implement user authentication",
      "project_name": "Company Website",
      "time_today": 90,
      "total_time": 145,
      "sessions_count": 2,
      "status": "in_progress",
      "has_active_timer": false
    },
    {
      "task_id": "uuid-task-2", 
      "task_title": "Fix responsive design",
      "project_name": "Company Website",
      "time_today": 55,
      "total_time": 55,
      "sessions_count": 1,
      "status": "in_progress",
      "has_active_timer": true
    }
  ]
}
```

### 🔐 Time Tracking Permissions Summary

| Action | Admin | Internal Staff | Client |
|---|:---:|:---:|:---:|
| Start/Stop timer | ✅ (any task) | ✅ (assigned tasks) | ❌ |
| View time logs | ✅ (all logs) | ✅ (own logs) | ❌ |
| View time summary | ✅ (all users) | ✅ (own summary) | ❌ |
| See time totals in tasks | ✅ | ✅ | ✅ (via tickets) |
| View active timers | ✅ (all projects) | ✅ (assigned tasks) | ✅ (own projects) |

---

## 🔄 Recent Updates

### Version 2.1.0 (January 2025) - Time Tracking Release
- ✅ **COMPREHENSIVE TIME TRACKING** - Full time monitoring system for tasks and projects
- ✅ **SESSION-BASED TIMERS** - Start/stop functionality with detailed session logging
- ✅ **JSONB STORAGE** - Flexible time log storage with automatic aggregation
- ✅ **ROLE-BASED TIME ACCESS** - Admin oversight and staff self-monitoring
- ✅ **BILLING SUPPORT** - Accurate time data for project billing and reporting
- ✅ **ACTIVE TIMER MANAGEMENT** - Prevent overlapping sessions and ensure data integrity

#### ⏱️ Time Tracking Features:
- `POST /tasks/{id}/timer/start` - Start timer for task (admin/staff)
- `POST /tasks/{id}/timer/stop` - Stop timer and calculate duration
- `GET /tasks/{id}/time-logs` - Detailed session logs and analytics
- `GET /tasks/my/time-summary` - Personal time tracking dashboard
- Automatic `total_time_minutes` and `time_sessions_count` calculation
- Client visibility of time investment through existing ticket endpoints

#### 🔧 Technical Improvements:
- Enhanced database schema with `time_logs` JSONB column
- Robust session management with validation and cleanup
- Integration with existing task assignment and permission systems
- Support for multi-user time tracking on shared tasks

#### 🔄 Workflow Improvements:
- **Simplified Ticket Status Flow**: `to_read` → `accepted` (when tasks created) or `rejected`
- **Automatic Status Updates**: Ticket status changes to `accepted` when admin creates tasks
- **Clearer Client Communication**: Clients see clear "accepted" status instead of "processing"
- **Improved Admin Workflow**: Direct task creation moves tickets to accepted state

### Version 2.0.0 (August 2025) - Major Release
- ✅ **COMPLETE CLIENT PORTAL** - Full client-facing API with project and ticket management
- ✅ **ADVANCED TICKET SYSTEM** - Clients can create tickets and monitor task progress
- ✅ **ADMIN DASHBOARD** - Real-time statistics and system insights
- ✅ **ENHANCED PROJECT MANAGEMENT** - Full CRUD operations with client assignments
- ✅ **TASK PROGRESS MONITORING** - Clients can see detailed task progress and assignments
- ✅ **MULTI-ROLE WORKFLOWS** - Complete workflows for admin, staff, and client interactions
- ✅ **COMPREHENSIVE API** - 20+ endpoints for complete system management

### Major Features Added:

#### 📈 Admin Dashboard & Analytics
- `GET /admin/dashboard` - Real-time system statistics
- `GET /admin/users/clients` - Enhanced client management with project counts
- Complete system oversight and monitoring capabilities

#### 👤 Client Portal & Communication
- `GET /client/projects` - Client project visibility
- `GET /client/projects/{id}` - Detailed project information
- `POST /client/projects/{id}/tickets` - Ticket creation system
- `GET /client/tickets` - Comprehensive ticket management
- `GET /client/tickets/{id}` - Detailed ticket information with tasks
- `GET /client/projects/{id}/tickets/{id}/tasks` - Complete task progress monitoring

#### 🏗️ Enhanced Project Management
- `POST /admin/projects` - Project creation with client assignment
- Advanced project listing with client relations and ticket statistics
- Complete project lifecycle management

#### 🔄 Workflow Improvements
- **Admin Workflow**: Complete system management, user creation, project oversight
- **Staff Workflow**: Task assignment, progress tracking, collaboration tools
- **Client Workflow**: Project monitoring, ticket creation, progress visibility

#### 🔐 Security & Privacy
- Role-based access control for all endpoints
- Client data isolation and ownership verification
- Privacy controls for sensitive staff information
- Comprehensive input validation and error handling

#### 📊 Database Optimizations
- Efficient query design for complex relationships
- Optimized database functions for better performance
- Comprehensive error handling and logging

### Technical Improvements:
- **20+ API endpoints** for complete system functionality
- **Advanced database queries** with proper relationship handling
- **Enhanced security model** with role-based permissions
- **Comprehensive documentation** with workflow examples
- **Performance optimizations** for multi-role access patterns
- **Privacy controls** protecting sensitive information

---

## 🚀 Roadmap & Future Features

### Planned Enhancements (v2.1.0)
- 🔔 **Real-time Notifications** - WebSocket integration for live updates
- 📱 **Mobile Push Notifications** - Flutter integration for task updates
- 📄 **File Upload System** - Document and asset management for projects
- 🕒 **Time Tracking** - Task duration tracking and reporting
- 📊 **Advanced Analytics** - Detailed project performance metrics
- 💬 **Comment System** - Threaded discussions on tickets and tasks
- 🔍 **Advanced Search** - Full-text search across projects, tickets, and tasks

### Potential Features (v3.0.0)
- 📅 **Calendar Integration** - Project timeline and milestone tracking
- 🎨 **Customizable Dashboards** - Role-specific dashboard layouts
- 🔗 **Third-party Integrations** - Slack, Teams, GitHub integration
- 📈 **Client Billing Module** - Time-based billing and invoicing
- 🌐 **Multi-language Support** - Internationalization for global teams
- 🎯 **Project Templates** - Predefined project structures and workflows

---

## 🤝 Contributing

This project is part of my portfolio demonstrating full-stack development capabilities. While it's primarily a showcase project, feedback and suggestions are welcome.

### Contact Information
- **Developer**: Andrea La Torre
- **Portfolio**: [GitHub Profile](https://github.com/latorreandrea)
- **Frontend Repository**: [Flutter Mobile App](https://github.com/latorreandrea/auravisual-collab-manager-mobile)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **FastAPI** - For the excellent web framework
- **Supabase** - For the powerful backend-as-a-service platform
- **Flutter** - For the cross-platform mobile development framework
- **VS Code** - For the outstanding development environment

---

**Built with ❤️ by Andrea La Torre**

*Demonstrating modern full-stack development with Python, FastAPI, Supabase, and Flutter*


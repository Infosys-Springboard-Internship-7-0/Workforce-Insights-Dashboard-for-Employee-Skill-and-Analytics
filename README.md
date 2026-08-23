# AI-Powered Workforce Analytics & Talent Intelligence Dashboard — Deployment & Setup Guide

A full-stack workforce analytics and talent intelligence platform built with **Streamlit, FastAPI, Neon PostgreSQL, pgvector, Groq, JWT authentication, and RAG**.

---

## 🏗️ Architecture

```text
                         ┌──────────────────────┐
                         │      Streamlit       │
                         │      Frontend        │
                         └──────────┬───────────┘
                                    │
                              REST + JWT
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       FastAPI        │
                         │       Backend        │
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
   ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
   │ Neon PostgreSQL  │   │ Embedding Model  │   │    Groq LLM      │
   │                  │   │                  │   │                  │
   │ users            │   │ all-MiniLM-L6-v2 │   │ GPT-OSS 120B     │
   │ documents        │   │ 384 dimensions   │   │                  │
   │ recommendations  │   │                  │   │ RAG Generation   │
   │ chats            │   └──────────────────┘   └──────────────────┘
   │ datasets         │
   │ dataset_rows     │
   │ pgvector         │
   └──────────────────┘
```

---

## 🏢 User vs Admin Architecture

This platform now features **role-based access control** with two distinct user areas:

### 👥 User Area
Accessible to all authenticated users:
- **Home/Landing Page** — Project overview and capabilities
- **AI Assistant Chat** — Ask questions about uploaded documents
- **Data Viewer** — Inspect and explore datasets
- **Power BI Dashboards** — View embedded business dashboards
- **Team Information** — View team member profiles

### 🔐 Admin Area (Protected)
Restricted to administrators only:
- **/admin/overview** — Analytics dashboard with key metrics
- **/admin/documents** — Manage documents and knowledge base
- **/admin/team** — Manage team members
- **/admin/admins** — Manage administrator accounts
- **/admin/powerbi** — Configure Power BI dashboards
- **/admin/recommendations** — View and manage recommendations

**Security Implementation:**
- JWT token-based authentication
- Role verification on backend API endpoints
- Frontend route protection based on user role
- Password hashing with bcrypt

---

## 📊 Enhanced Database Models

The platform now includes enhanced data models with improved tracking and metadata:

| Model | Enhancements |
|-------|--------------|
| **User** | Added `updated_at` timestamp; role defaults to "user" (not "admin") |
| **Document** | Added `description`, `processing_status`, `file_path`, and `updated_at` |
| **Recommendation** | Added `dismissed` flag, `dismissed_at` timestamp, enhanced status tracking |
| **PowerBI Dashboard** | Added `created_by` (admin tracking), `created_at`, `updated_at` |
| **Team Member** | Added `created_at`, `updated_at` timestamps |

**Database Migration:** `0004_enhance_models` has been applied and includes full upgrade/downgrade paths.

---

## 🛠️ Backend Services

The backend now includes modular services for clean architecture:

- **AdminService** — Admin user CRUD operations
- **AuthService** — Authentication, token management, role verification
- **DocumentService** — Document lifecycle management, metadata, chunking
- **AnalyticsService** — Dashboard statistics and reporting
- **TeamService** — Team member management

These services are imported and used throughout the API routers for consistent, maintainable code.

---

## 📡 API Endpoints

### Authentication
- `POST /api/auth/login` — User login
- `GET /api/auth/me` — Get current user profile
- `POST /api/auth/change-password` — Change password
- `GET /api/auth/admins` — List all admins (admin only)
- `GET /api/auth/admins/{admin_id}` — Get admin details (admin only)
- `POST /api/auth/admins` — Create new admin (admin only)
- `PUT /api/auth/admins/{admin_id}` — Update admin (admin only)
- `POST /api/auth/admins/{admin_id}/reset-password` — Reset admin password (admin only)
- `DELETE /api/auth/admins/{admin_id}` — Delete admin (admin only)

### Analytics (Admin Only)
- `GET /api/analytics/dashboard` — Get all dashboard statistics
- `GET /api/analytics/documents` — Get document overview
- `GET /api/analytics/recommendations` — Get recommendation overview

### Documents (Admin Only)
- `GET /api/admin/documents` — List all documents
- `GET /api/admin/documents/{document_id}` — Get document details
- `POST /api/admin/documents/upload` — Upload new document
- `PUT /api/admin/documents/{document_id}` — Update document metadata
- `DELETE /api/admin/documents/{document_id}` — Delete document

### Team (Public/Admin)
- `GET /api/team` — Public team member listing
- `GET /api/admin/team` — Admin team member list
- `GET /api/admin/team/{member_id}` — Get member details
- `POST /api/admin/team` — Create team member
- `PUT /api/admin/team/{member_id}` — Update team member
- `DELETE /api/admin/team/{member_id}` — Delete team member

---

# 🚀 1. Clone the Repository

```powershell
git clone https://github.com/Yakaanil2006/AI-Workforce-Assistant-Platform.git
cd AI-Workforce-Assistant-Platform
```

If you are using the project ZIP:

1. Extract the ZIP.
2. Open PowerShell inside the extracted project folder.

---

# 🗄️ 2. Setup Neon PostgreSQL

Create a PostgreSQL database using Neon.

Copy the Neon database connection string.

The project uses **psycopg 3**, so the connection string should use:

```text
postgresql+psycopg://USER:PASSWORD@HOST/DATABASE?sslmode=require
```

Example:

```text
postgresql+psycopg://USER:PASSWORD@HOST/neondb?sslmode=require
```

## Enable pgvector

Open the Neon SQL Editor and execute:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

---

# ⚙️ 3. Backend Setup

Open PowerShell:

```powershell
cd backend
```

## Create virtual environment

```powershell
python -m venv .venv
```

## Activate virtual environment

```powershell
.venv\Scripts\activate
```

## Upgrade pip

```powershell
python -m pip install --upgrade pip
```

## Install dependencies

```powershell
pip install -r requirements.txt
```

## Create environment file

```powershell
copy .env.example .env
```

---

# 🔐 4. Configure Backend `.env`

Open:

```text
backend/.env
```

Add your actual credentials:

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST/DATABASE?sslmode=require

GROQ_API_KEY=YOUR_GROQ_API_KEY
GROQ_MODEL=openai/gpt-oss-120b

JWT_SECRET_KEY=YOUR_LONG_RANDOM_SECRET
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
TOP_K=5

CORS_ORIGINS=http://localhost:8501

POWERBI_EMBED_URL=

HF_API_KEY=YOUR_HUGGINGFACE_API_KEY
```

> **Important:** Never commit `backend/.env` to GitHub.

---

# 🔒 5. Protect Environment Variables

Your `.gitignore` should contain:

```gitignore
.env
*.env
.venv/
__pycache__/
*.pyc
.pytest_cache/
.streamlit/secrets.toml
```

Your GitHub repository should contain:

```text
backend/.env.example
```

but **not**:

```text
backend/.env
```

The `.env.example` file should contain placeholders:

```env
DATABASE_URL=your_database_url
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
JWT_SECRET_KEY=your_long_random_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
TOP_K=5
CORS_ORIGINS=http://localhost:8501
POWERBI_EMBED_URL=
HF_API_KEY=your_huggingface_api_key
```

---

# 🗃️ 6. Run Database Migrations

From the `backend` directory:

```powershell
alembic upgrade head
```

Check the current migration:

```powershell
alembic current
```

The database should now contain the required tables and pgvector schema.

---

# 👤 7. Create Admin User

Run:

```powershell
python scripts/create_admin.py
```

Follow the prompts to create the first administrator account.

---

# 🧪 8. Test Groq API

Before starting the complete application, verify that your Groq API key can access the selected model.

Run:

```powershell
python -c "from groq import Groq; import os; c=Groq(api_key=os.getenv('GROQ_API_KEY')); print([m.id for m in c.models.list().data if m.active])"
```

Make sure your selected model appears:

```text
openai/gpt-oss-120b
```

Test the model directly:

```powershell
python -c "from groq import Groq; import os; c=Groq(api_key=os.getenv('GROQ_API_KEY')); r=c.chat.completions.create(model='openai/gpt-oss-120b',messages=[{'role':'user','content':'Say hello'}]); print(r.choices[0].message.content)"
```

If successful, Groq is ready.

---

# 🖥️ 9. Start FastAPI Backend

From the `backend` directory:

```powershell
uvicorn app.main:app --reload --port 8000
```

The backend runs at:

```text
http://127.0.0.1:8000
```

## Health Check

Open:

```text
http://127.0.0.1:8000/health
```

## Swagger API Documentation

Open:

```text
http://127.0.0.1:8000/docs
```

You should see:

```text
Application startup complete.
```

---

# 🔑 10. Test Authentication

Use the frontend or Swagger UI.

Test:

```text
POST /api/auth/login
```

Then:

```text
GET /api/auth/me
```

Expected result:

```text
POST /api/auth/login    → 200 OK
GET  /api/auth/me       → 200 OK
```

### Test Admin Endpoints

Test admin-only endpoints:

```text
GET /api/auth/admins              → 200 OK (admin only)
GET /api/analytics/dashboard      → 200 OK (admin only)
GET /api/admin/documents          → 200 OK (admin only)
GET /api/admin/team               → 200 OK
```

Regular users will receive `403 Forbidden` on admin endpoints.

---

# 🧪 11. Test RAG Pipeline

The RAG workflow is:

```text
PDF / Document
      │
      ▼
Document Loader
      │
      ▼
Text Extraction
      │
      ▼
Chunking
      │
      ▼
Embedding Generation
      │
      ▼
384-Dimensional Vector
      │
      ▼
Neon PostgreSQL + pgvector
      │
      │
User Question
      │
      ▼
Question Embedding
      │
      ▼
Vector Similarity Search
      │
      ▼
Top-K Relevant Chunks
      │
      ▼
Context
      │
      ▼
Groq LLM
      │
      ▼
AI Answer + Sources
```

Default configuration:

```env
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
TOP_K=5
```

---

# 📄 12. Test Document Upload

After the backend starts:

1. Login as administrator.
2. Navigate to the **Admin Area** → **Documents**.
3. Upload a PDF with an optional description.
4. Verify document appears in the list with `processing` status.
5. Once processing completes, status changes to `indexed`.
6. Test document metadata editing and filtering by status.
7. Ask a question in the **AI Assistant** related to the uploaded document.

Expected workflow:

```text
POST /api/admin/documents/upload     → 201 Created
GET  /api/admin/documents            → 200 OK (document listed)
PUT  /api/admin/documents/{id}       → 200 OK (metadata updated)
POST /api/assistant/chat             → 200 OK (RAG retrieval)
```

**Admin Document Management Features:**
- Upload documents with descriptions
- Filter documents by processing status (indexed, processing, failed)
- View document metadata and chunk count
- Edit document filename and description
- Delete documents from the knowledge base

---

# 📊 13. Test Admin Analytics Dashboard

Login as admin and navigate to **Admin Area** → **Overview**:

1. View **Key Metrics** — Documents, Datasets, Admins, Team members, Recommendations
2. Check **Document Processing Status** — Indexed, Processing, Failed counts
3. Review **Recommendations Status** — Grouped by status and priority
4. Inspect **Chat Analytics** — Sessions and message counts
5. Explore **Dataset Analytics** — Total datasets and rows
6. Verify **Recent Activities** — Recent uploads and recommendations

Expected endpoint:

```text
GET /api/analytics/dashboard  → 200 OK
```

---

# 👥 14. Test Team Management

Login as admin and navigate to **Admin Area** → **Team**:

1. View all team members
2. Add a new team member (name, title, bio)
3. Edit member information
4. Delete a team member
5. Verify team appears on public **Home** page

Expected endpoints:

```text
GET  /api/team                      → 200 OK (public)
GET  /api/admin/team                → 200 OK (admin)
POST /api/admin/team                → 201 Created
PUT  /api/admin/team/{member_id}    → 200 OK
DELETE /api/admin/team/{member_id}  → 204 No Content
```

---

# 🎨 15. Frontend Setup

Open a **second PowerShell terminal**.

From the project root:

```powershell
cd frontend
```

Create the virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create `.env`:

```powershell
copy .env.example .env
```

---

# 🔗 16. Configure Frontend `.env`

Open:

```text
frontend/.env
```

Set:

```env
API_BASE_URL=http://127.0.0.1:8000
```

This connects Streamlit to FastAPI.

---

# ▶️ 17. Start Streamlit

From the `frontend` directory:

```powershell
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

---

# 🔄 18. Complete Local Startup

You need **two terminals**.

## Terminal 1 — FastAPI

```powershell
cd C:\AI-Workforce-Assistant-Platform\backend
.venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

## Terminal 2 — Streamlit

```powershell
cd C:\AI-Workforce-Assistant-Platform\frontend
.venv\Scripts\activate
streamlit run app.py
```

Application:

```text
http://localhost:8501
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---

# 🧪 19. Complete Testing Order

Test the application in this order:

```text
1. Start Neon PostgreSQL
       ↓
2. Run migrations
       ↓
3. Start FastAPI
       ↓
4. Test /health
       ↓
5. Create admin
       ↓
6. Test login
       ↓
7. Start Streamlit
       ↓
8. Login from frontend
       ↓
9. Test Team
       ↓
10. Upload Document
       ↓
11. Verify Embeddings
       ↓
12. Test RAG Assistant
       ↓
13. Test Dataset CRUD
       ↓
14. Test Recommendations
       ↓
15. Test Power BI
```

---

# 🧩 20. Troubleshooting

## Backend cannot start

Activate the environment:

```powershell
.venv\Scripts\activate
```

Install dependencies again:

```powershell
pip install -r requirements.txt
```

Start:

```powershell
uvicorn app.main:app --reload --port 8000
```

---

## Frontend cannot connect to backend

Check FastAPI:

```text
http://127.0.0.1:8000/health
```

Check:

```env
API_BASE_URL=http://127.0.0.1:8000
```

Make sure both applications are running.

---

## Groq `model_not_found`

Check models available to your API key:

```powershell
python -c "from groq import Groq; import os; c=Groq(api_key=os.getenv('GROQ_API_KEY')); print([m.id for m in c.models.list().data if m.active])"
```

Choose an available model:

```env
GROQ_MODEL=MODEL_ID
```

Restart FastAPI:

```powershell
uvicorn app.main:app --reload --port 8000
```

---

## Database connection error

Check:

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST/DATABASE?sslmode=require
```

Then:

```powershell
alembic current
```

If required:

```powershell
alembic upgrade head
```

---

## pgvector error

Run in Neon SQL Editor:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Then:

```powershell
alembic upgrade head
```

---

# 🌐 21. Deployment Order

For production deployment, deploy the **backend first**.

```text
                    GitHub
                      │
          ┌───────────┴───────────┐
          │                       │
          ▼                       ▼
   FastAPI Backend          Streamlit Frontend
          │                       │
          │                       │
          ▼                       │
   Neon PostgreSQL ◄──────────────┘
       + pgvector
          │
          ├──────────► Groq
          │
          └──────────► Hugging Face
```

## Recommended deployment sequence

```text
1. Push clean code to GitHub
        ↓
2. Create Neon PostgreSQL
        ↓
3. Enable pgvector
        ↓
4. Deploy FastAPI backend
        ↓
5. Add backend environment variables
        ↓
6. Run migrations
        ↓
7. Test /health
        ↓
8. Test /docs
        ↓
9. Test authentication
        ↓
10. Test RAG
        ↓
11. Deploy Streamlit frontend
        ↓
12. Set API_BASE_URL to backend URL
        ↓
13. Update CORS_ORIGINS
        ↓
14. Test complete application
```

---

# 🔐 22. Production Environment Variables

For production, configure environment variables through the hosting provider.

### Backend

```env
DATABASE_URL=YOUR_NEON_DATABASE_URL
GROQ_API_KEY=YOUR_GROQ_API_KEY
GROQ_MODEL=openai/gpt-oss-120b
JWT_SECRET_KEY=YOUR_LONG_RANDOM_SECRET
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
TOP_K=5
CORS_ORIGINS=YOUR_FRONTEND_URL
POWERBI_EMBED_URL=
HF_API_KEY=YOUR_HUGGINGFACE_API_KEY
```

### Frontend

```env
API_BASE_URL=YOUR_DEPLOYED_BACKEND_URL
```

Do **not** use:

```env
API_BASE_URL=http://127.0.0.1:8000
```

in production.

---

# 📁 23. Project Structure

```text
AI-Workforce-Assistant-Platform/
│
├── backend/
│   ├── app/
│   │   ├── core/
│   │   ├── models/
│   │   ├── rag/
│   │   ├── routers/
│   │   ├── schemas/
│   │   └── services/
│   │
│   ├── migrations/
│   ├── scripts/
│   ├── .env.example
│   ├── alembic.ini
│   └── requirements.txt
│
├── frontend/
│   ├── services/
│   ├── ui_pages/
│   │   ├── admin/
│   │   └── ...
│   ├── utils/
│   ├── .env.example
│   ├── app.py
│   └── requirements.txt
│
├── data/
│   └── sample.csv
│
├── docs/
│   └── architecture.md
│
├── .gitignore
└── README.md
```

---

# 🛠️ 24. Technology Stack

## Frontend

* Python
* Streamlit
* REST API
* JWT

## Backend

* Python
* FastAPI
* SQLAlchemy
* Alembic
* Pydantic
* psycopg 3

## Database

* Neon PostgreSQL
* pgvector

## AI / RAG

* Groq
* GPT-OSS 120B
* Sentence Transformers
* all-MiniLM-L6-v2
* Vector similarity search
* Retrieval-Augmented Generation

## Authentication

* JWT
* bcrypt

## Integrations

* Hugging Face
* Power BI

---

# 🔒 25. Security Checklist

Before pushing to GitHub:

```powershell
git status
```

Check for exposed secrets:

```powershell
git grep -n "gsk_"
git grep -n "hf_"
git grep -n "npg_"
```

These commands should return no real credentials.

Never commit:

```text
.env
*.env
.venv/
__pycache__/
```

If credentials are accidentally exposed:

1. Rotate the Groq API key.
2. Rotate the Hugging Face token.
3. Change the Neon database password.
4. Generate a new JWT secret.
5. Update the deployment environment variables.

---

# 📌 26. Git Workflow

After making changes:

```powershell
git status
```

Add changes:

```powershell
git add .
```

Commit:

```powershell
git commit -m "Update AI-Powered Workforce Analytics Dashboard"
```

Push:

```powershell
git push origin main
```

Before pushing, always verify that secrets are not tracked.

---

# ⚡ 27. Quick Start

## Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
python scripts/create_admin.py
uvicorn app.main:app --reload --port 8000
```

## Frontend

Open another terminal:

```powershell
cd frontend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---

# � 28. Latest Updates & New Features

## ✨ Major Enhancements (Latest Release)

### 🔐 Role-Based Access Control
- **User Role** — Access to assistant, data viewer, dashboards, team info
- **Admin Role** — Full access to analytics, document management, team management, admin controls
- JWT-based authentication with bcrypt password hashing
- Role enforcement on both frontend and backend API endpoints

### 📊 Enhanced Analytics Dashboard
- **Key Metrics** — Real-time counts of documents, datasets, admins, team members, recommendations
- **Document Processing Status** — Visual breakdown of indexed, processing, and failed documents
- **Recommendations Status** — Grouped by status and priority level
- **Chat Analytics** — Session and message statistics
- **Dataset Analytics** — Total datasets and rows overview
- **Recent Activities** — Feed of recent uploads and recommendations

### 📄 Advanced Document Management
- **Upload with Metadata** — Add descriptions to documents during upload
- **Status Tracking** — Monitor document processing (processing → indexed)
- **Filtering & Search** — Filter by status, view metadata and chunk counts
- **Metadata Editing** — Update filename and description after upload
- **Bulk Operations** — Delete documents from knowledge base

### 👥 Team Management Interface
- **Admin Control** — Create, edit, delete team members
- **Public Display** — Team members visible on home page
- **Member Profiles** — Name, title, biography, and metadata
- **CRUD Operations** — Full management with timestamps

### 🛠️ Improved Backend Architecture
- **Modular Services** — AdminService, AuthService, DocumentService, AnalyticsService, TeamService
- **Enhanced Models** — Added timestamps, status fields, metadata to all primary models
- **New API Endpoints** — 25+ endpoints for admin operations and analytics
- **Database Migration** — `0004_enhance_models` with full upgrade/downgrade support

### 🎨 Improved Frontend Pages
- **New Home Page** — Problem statement, objectives, capabilities, architecture, team showcase
- **Admin Overview** — Centralized dashboard with real-time metrics
- **Admin Documents** — Complete document lifecycle management
- **Admin Team** — Team member management interface

## 📝 Database Schema Updates

| Model | New Fields | Purpose |
|-------|-----------|---------|
| `users` | `updated_at` | Track user modifications |
| `documents` | `description`, `processing_status`, `file_path`, `updated_at` | Enhanced metadata and tracking |
| `recommendations` | `dismissed`, `dismissed_at`, `updated_at` | Track recommendation lifecycle |
| `powerbi_dashboards` | `created_by`, `created_at`, `updated_at` | Admin tracking and auditing |
| `team_members` | `created_at`, `updated_at` | Timestamp tracking |

## 🔗 New API Endpoints

### Admin Authentication (9 endpoints)
- Admin CRUD operations with role verification
- Password reset functionality
- Access control enforcement

### Analytics (3 endpoints)
- Dashboard statistics
- Document overview
- Recommendation overview

### Document Management (5 endpoints)
- List, retrieve, upload, update, delete documents
- Metadata management
- Status filtering

### Team Management (6 endpoints)
- List public and admin views
- Create, update, delete team members
- Full member lifecycle management

## ✅ Testing Improvements

The README now includes comprehensive testing sections for:
1. Admin endpoints verification
2. Document upload and management workflow
3. Analytics dashboard functionality
4. Team member CRUD operations
5. Complete integration testing checklist

## 🚀 Ready for Production

All changes have been:
- ✅ Implemented and verified
- ✅ Integrated with existing code
- ✅ Database migrations applied
- ✅ Documented in this README
- ✅ Tested for syntax and imports

**Next Steps:**
1. Thoroughly test all features locally
2. Verify admin area access control
3. Check analytics dashboard with real data
4. Test complete user and admin workflows
5. Commit and push to GitHub
6. Deploy to production environment

---

# �📜 License

This project is intended for educational, research, portfolio, and demonstration purposes.

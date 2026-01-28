# AI Agent Identity & Access Gateway

A production-grade backend system that treats AI agents as first-class identities with authentication, authorization, observability, and lifecycle controls.

## What This Project Demonstrates

1. **Backend Development**: FastAPI, REST APIs, async Python
2. **Authentication & Authorization**: OAuth2, JWT tokens, scoped permissions
3. **AI/ML Integration**: RAG pipelines, vector databases, LangChain
4. **DevOps**: Docker containerization, observability, logging
5. **Security**: Access control, credential rotation, audit logs

## Core Concept

Every AI agent is treated like a user:
- Must authenticate with credentials
- Has scoped permissions (read/write/execute)
- All actions are logged and auditable
- Access can be revoked or rotated

## Architecture Overview

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
┌──────▼──────────────────────┐
│   API Gateway (FastAPI)     │
│   - Authentication          │
│   - Authorization           │
│   - Request Routing         │
└──────┬──────────────────────┘
       │
┌──────▼──────────┬───────────────┬──────────────┐
│                 │               │              │
│  Agent Manager  │  RAG Engine   │  Audit Log   │
│  - Register     │  - Embeddings │  - Tracing   │
│  - Credentials  │  - Vector DB  │  - Metrics   │
│  - Permissions  │  - Query      │              │
└─────────────────┴───────────────┴──────────────┘
```

## Tech Stack

- **Backend**: Python 3.11+ with FastAPI
- **Auth**: OAuth2 with JWT tokens
- **Database**: PostgreSQL (agent metadata) + FAISS/Pinecone (vectors)
- **AI/ML**: LangChain, OpenAI embeddings
- **Observability**: OpenTelemetry, structured logging
- **Infrastructure**: Docker, Docker Compose

## Project Structure

```
identityRAG/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── auth/                # Authentication & authorization
│   │   ├── __init__.py
│   │   ├── jwt.py           # JWT token handling
│   │   ├── oauth2.py        # OAuth2 flows
│   │   └── permissions.py   # Permission/scope logic
│   ├── agents/              # Agent lifecycle management
│   │   ├── __init__.py
│   │   ├── models.py        # Agent data models
│   │   ├── service.py       # Business logic
│   │   └── routes.py        # API endpoints
│   ├── rag/                 # RAG pipeline
│   │   ├── __init__.py
│   │   ├── embeddings.py    # Vector embeddings
│   │   ├── vectorstore.py   # Vector database interface
│   │   └── routes.py        # RAG query endpoints
│   ├── observability/       # Logging, tracing, metrics
│   │   ├── __init__.py
│   │   ├── logging.py
│   │   └── tracing.py
│   └── database/            # Database models and connections
│       ├── __init__.py
│       └── models.py
├── tests/                   # Test suite
├── docker/                  # Docker configurations
├── docs/                    # Additional documentation
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── docker-compose.yml      # Local development setup
```

## Getting Started

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- OpenAI API key (for embeddings)

### Installation

1. Clone and enter the directory:
```bash
cd identityRAG
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new agent
- `POST /auth/login` - Authenticate and get JWT access token
- `GET /auth/me` - Get current authenticated agent info (protected)
- `POST /auth/revoke/{agent_id}` - Deactivate an agent

### Demo Endpoints (Scope-Based Authorization)
- `GET /auth/demo/read-only` - No scope required (just authentication)
- `GET /auth/demo/write-protected` - Requires 'write' scope
- `GET /auth/demo/admin-only` - Requires 'admin' scope
- `GET /auth/demo/multi-scope` - Requires both 'read' AND 'write' scopes

### Observability
- `GET /` - API information
- `GET /health` - Health check
- `GET /health/ready` - Readiness check

### Coming Soon
- Agent Management (list, update, delete)
- RAG Operations (upload documents, query knowledge base)
- Audit logs and tracing

## Development Roadmap

- [x] Project structure
- [x] Basic FastAPI server with health checks
- [x] JWT authentication system
- [x] Agent registration and credential management
- [x] Scope-based authorization (demo endpoints)
- [ ] RAG pipeline with vector database
- [ ] Access control for documents
- [ ] Audit logging and tracing
- [ ] OpenTelemetry observability
- [ ] Docker containerization
- [ ] Kubernetes (optional)

## Testing

### Quick Start
Run the server:
```bash
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

Visit the interactive API docs:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

### Test Scripts

**Basic Authentication Test:**
```bash
./test_auth.sh
```

**Scope-Based Authorization Demo:**
```bash
./test_scopes.sh
```

This creates agents with different permission levels and demonstrates:
- Reader agent (read-only access)
- Writer agent (read + write access)
- Admin agent (full access)
- How scopes control endpoint access

### Manual Testing Examples

**Register an agent:**
```bash
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-agent",
    "password": "SecurePass123",
    "scopes": ["read", "write"]
  }'
```

**Login and get token:**
```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"name": "my-agent", "password": "SecurePass123"}'
```

**Access protected endpoint:**
```bash
TOKEN="your-jwt-token-here"
curl -H "Authorization: Bearer $TOKEN" http://localhost:8001/auth/me
```

## Learning Resources

This project covers concepts from:
- Authentication: OAuth2, JWT, token-based auth
- AI/ML: Embeddings, vector similarity, RAG
- DevOps: Containerization, observability, infrastructure as code
- Security: Principle of least privilege, audit trails, credential rotation

---

Built as a portfolio project demonstrating production-grade AI infrastructure.

# AI Agent Identity & Access Gateway

A production-grade backend system that treats AI agents as first-class identities with authentication, authorization, observability, and lifecycle controls.

## What This Project Teaches

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
- `POST /auth/token` - Get access token
- `POST /auth/revoke` - Revoke agent credentials

### Agent Management
- `GET /agents` - List all agents
- `GET /agents/{agent_id}` - Get agent details
- `PUT /agents/{agent_id}/permissions` - Update permissions
- `DELETE /agents/{agent_id}` - Deactivate agent

### RAG Operations
- `POST /rag/documents` - Upload documents (requires write permission)
- `POST /rag/query` - Query knowledge base (requires read permission)
- `GET /rag/documents` - List documents

### Observability
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics
- `GET /audit/{agent_id}` - Get agent audit logs

## Development Roadmap

- [x] Project structure
- [ ] Basic FastAPI server
- [ ] JWT authentication
- [ ] Agent registration
- [ ] Permission system
- [ ] RAG pipeline
- [ ] Access control
- [ ] Audit logging
- [ ] Observability
- [ ] Docker setup
- [ ] Kubernetes (optional)

## Learning Resources

This project covers concepts from:
- Authentication: OAuth2, JWT, token-based auth
- AI/ML: Embeddings, vector similarity, RAG
- DevOps: Containerization, observability, infrastructure as code
- Security: Principle of least privilege, audit trails, credential rotation

---

Built as a portfolio project demonstrating production-grade AI infrastructure.

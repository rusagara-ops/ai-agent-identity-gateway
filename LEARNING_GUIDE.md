# 🎓 Complete Learning Guide: AI Agent Identity Gateway

This document explains every concept, every file, and every design decision in detail.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Concepts](#core-concepts)
3. [File-by-File Deep Dive](#file-by-file-deep-dive)
4. [How Authentication Works](#how-authentication-works)
5. [Security Deep Dive](#security-deep-dive)
6. [Common Questions](#common-questions)

---

## Architecture Overview

### The Request Flow

```
Client (Postman/curl)
    ↓
    | 1. HTTP Request (POST /auth/login)
    ↓
FastAPI Server (app/main.py)
    ↓
    | 2. Route to handler (app/auth/routes.py)
    ↓
Authentication Logic
    ↓
    | 3. Query database (app/database/models.py)
    | 4. Verify password (app/auth/security.py)
    | 5. Generate JWT token
    ↓
Response (JWT token)
    ↓
Client stores token
    ↓
    | 6. Subsequent requests include token
    ↓
Protected Endpoint
    ↓
    | 7. Dependency extracts token (app/auth/dependencies.py)
    | 8. Validates token
    | 9. Loads agent from database
    ↓
Route Handler (has access to authenticated agent)
    ↓
Response
```

### Component Responsibilities

| Component | What It Does | Analogy |
|-----------|-------------|---------|
| **config.py** | Loads settings from .env | Building blueprints/configuration |
| **main.py** | Entry point, starts server | Front door of the building |
| **database/models.py** | Database schema | Filing cabinet structure |
| **auth/security.py** | Password hashing, JWT creation | Vault that issues ID badges |
| **auth/schemas.py** | Request/response validation | Forms employees must fill out |
| **auth/dependencies.py** | Token validation middleware | Security guards at checkpoints |
| **auth/routes.py** | API endpoints | Different service desks |

---

## Core Concepts

### 1. What is FastAPI?

**FastAPI** is a modern Python web framework. Think of it as a restaurant:

- **The framework** = The kitchen and service system
- **Routes** (@app.get, @app.post) = Menu items
- **Route handlers** (async def) = Chefs who prepare dishes
- **Request body** = Customer's order
- **Response** = Finished dish

```python
@app.get("/menu")  # This is a route - like "GET me the menu"
async def get_menu():  # This is the handler - what happens when someone orders
    return {"items": ["burger", "pizza"]}  # This is the response
```

**Why async?**
- Regular functions: "I'll wait here until the food is ready" (blocking)
- Async functions: "I'll help other customers while the food cooks" (non-blocking)

In a web server, async lets you handle thousands of requests simultaneously!

---

### 2. What is a JWT (JSON Web Token)?

#### The Problem:
How does a server remember who you are without storing session data?

#### Traditional Approach (Sessions):
1. You log in
2. Server creates a session ID, stores it in a database
3. Server gives you the session ID as a cookie
4. On each request, server looks up the session ID in database

**Problem:** Server must store millions of sessions. Not scalable!

#### Modern Approach (JWT):
1. You log in
2. Server creates a **signed** token containing your info
3. Server gives you the token
4. On each request, server **verifies the signature** (no database lookup!)

**Benefit:** Server doesn't store anything. Scales infinitely!

#### JWT Structure:

A JWT looks like this:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

It has 3 parts separated by dots:
1. **Header** (algorithm info) - "This is signed with HS256"
2. **Payload** (data) - "This token is for agent ID 12345 with scopes [read, write]"
3. **Signature** (proof) - "I can prove this wasn't tampered with"

#### How Signing Works:

```
Signature = HMAC_SHA256(
    Header + Payload,
    SECRET_KEY  // Only the server knows this!
)
```

**Analogy:** It's like a sealed envelope with a wax stamp:
- Anyone can read the message (it's not encrypted)
- But only someone with the official stamp can create or modify it
- If anyone changes the message, the stamp won't match

---

### 3. What is Password Hashing?

#### The Problem:
If someone hacks your database, they can see all passwords!

#### Bad Solution:
Store encrypted passwords. Problem: If they get the encryption key, all passwords are exposed.

#### Good Solution (Hashing):
**Hashing is one-way encryption.** You CAN'T reverse it.

```
Password: "MySecret123"
   ↓ (bcrypt hash)
Stored: "$2b$12$KIXxKj2jF8sP9qL..."

// You cannot go backwards!
"$2b$12$KIXxKj2jF8sP9qL..." ↛ "MySecret123"  // IMPOSSIBLE
```

#### How Login Works:

```python
# Registration:
user_password = "MySecret123"
hashed = bcrypt.hash(user_password)  # "$2b$12$..."
database.save(hashed)

# Login:
user_enters = "MySecret123"
stored_hash = database.get_hash()
if bcrypt.verify(user_enters, stored_hash):  # ✓ Match!
    print("Correct password!")
```

**bcrypt.verify() internally:**
1. Takes the user's input: "MySecret123"
2. Hashes it with the same algorithm
3. Compares the resulting hash with stored hash
4. If they match, password is correct!

#### Why bcrypt specifically?

- **Slow on purpose!** Takes ~100ms to hash
- Prevents brute-force attacks (can only try 10 passwords/second)
- Regular hashing (like SHA256) is TOO FAST (millions/second)
- Includes a "salt" (random data) automatically

**Salt Example:**
```
"password123" + "random_salt_xyz" → hash1
"password123" + "random_salt_abc" → hash2  // Different!
```

This means even if two users have the same password, the hashes are different!

---

### 4. What is SQLAlchemy (ORM)?

**ORM = Object Relational Mapper**

It lets you use Python classes instead of SQL.

#### Without ORM (Raw SQL):
```python
cursor.execute("SELECT * FROM agents WHERE name = ?", (name,))
result = cursor.fetchone()
agent = {
    "id": result[0],
    "name": result[1],
    "hashed_password": result[2]
}
```

#### With ORM (SQLAlchemy):
```python
agent = db.query(Agent).filter(Agent.name == name).first()
# agent.id, agent.name, agent.hashed_password are all accessible!
```

**Benefits:**
- Type safety (your IDE knows what fields exist)
- No SQL injection vulnerabilities (automatically escaped)
- Database-agnostic (works with SQLite, PostgreSQL, MySQL, etc.)
- Automatic relationship handling

---

### 5. What are Pydantic Schemas?

**Pydantic** validates data and provides type hints.

#### Without Pydantic:
```python
def register_user(request_data: dict):
    name = request_data.get("name")  # What if it's missing?
    password = request_data.get("password")  # What if it's a number?
    # Manual validation hell!
```

#### With Pydantic:
```python
class UserCreate(BaseModel):
    name: str
    password: str

def register_user(user: UserCreate):
    # Pydantic already validated:
    # - name exists and is a string
    # - password exists and is a string
    # If not, FastAPI returns 422 error automatically!
```

**Extra Features:**
```python
class UserCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)  # Length validation
    password: str = Field(..., min_length=8)  # Minimum 8 characters
    email: Optional[str] = None  # Optional field
```

---

## File-by-File Deep Dive

### 📄 `.env` and `.env.example`

**Purpose:** Store configuration and secrets

**Why separate files?**
- `.env.example` → Committed to Git (safe template)
- `.env` → Never committed (contains real secrets)

**Key Settings:**

```bash
SECRET_KEY=78e9ee99...  # Used to sign JWTs
# Like a master key - if someone gets this, they can forge tokens!

DATABASE_URL=sqlite:///./identityrag.db
# Connection string for the database

ACCESS_TOKEN_EXPIRE_MINUTES=30
# How long tokens are valid (30 minutes)
```

**Why SQLite for now?**
- File-based database (no server needed)
- Perfect for development
- Production would use PostgreSQL

---

### 📄 `app/config.py`

**Purpose:** Load and validate environment variables

```python
class Settings(BaseSettings):
    secret_key: str  # Required (no default)
    api_port: int = 8001  # Optional (has default)
```

**What happens:**
1. Pydantic reads `.env` file
2. Validates types (is api_port an integer?)
3. Provides defaults for optional values
4. Creates a single `settings` object used everywhere

**The Singleton Pattern:**
```python
settings = Settings()  # Created once at startup
```

Every file imports this same instance:
```python
from app.config import settings
print(settings.api_port)  # 8001
```

**Benefits:**
- No magic strings scattered in code
- Type-safe (IDE auto-completion)
- Easy to change (just edit .env)

---

### 📄 `app/main.py`

**Purpose:** Application entry point

#### Key Sections:

**1. Creating the App:**
```python
app = FastAPI(
    title="AI Agent Identity Gateway",  # Shows in API docs
    docs_url="/docs"  # Automatic Swagger UI
)
```

**2. CORS Middleware:**
```python
app.add_middleware(CORSMiddleware, ...)
```

**What is CORS?**

Browsers have a security rule: "JavaScript on website A can't make requests to website B"

Example:
- Your React frontend runs on `localhost:3000`
- Your API runs on `localhost:8001`
- Without CORS, the browser blocks requests!

CORS middleware says: "localhost:3000 is allowed to call my API"

**3. Lifecycle Events:**
```python
@app.on_event("startup")
async def startup_event():
    # Runs once when server starts
    # Good for: connecting to database, loading ML models
```

**4. Including Routers:**
```python
app.include_router(auth_router)
```

This adds all routes from `auth_router` to the main app.
Think of it like plugging in a module.

---

### 📄 `app/database/models.py`

**Purpose:** Define database schema using SQLAlchemy ORM

#### Understanding the Agent Model:

```python
class Agent(Base):
    __tablename__ = "agents"  # SQL table name

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    # primary_key=True means this uniquely identifies each agent
    # UUID = Universally Unique Identifier (looks like: f02c1a50-f041-4814-91ee-10ae5350a133)

    name = Column(String, unique=True, index=True, nullable=False)
    # unique=True: No two agents can have the same name
    # index=True: Create a database index for fast lookups
    # nullable=False: This field is required

    scopes = Column(JSON, default=list)
    # Stores Python list as JSON: ["read", "write"]
```

**What happens when you create an agent:**

```python
new_agent = Agent(
    name="my-agent",
    hashed_password="$2b$12$...",
    scopes=["read"]
)
db.add(new_agent)  # Stages the change
db.commit()  # Executes: INSERT INTO agents VALUES (...)
```

**The get_db() function:**
```python
def get_db():
    db = SessionLocal()  # Create a database session
    try:
        yield db  # Give it to the route handler
    finally:
        db.close()  # Always close when done
```

This is a **dependency** that FastAPI uses:
```python
def my_route(db: Session = Depends(get_db)):
    # db is automatically created and closed
```

---

### 📄 `app/auth/security.py`

**Purpose:** Core security functions

#### 1. Password Hashing:

```python
def hash_password(password: str) -> str:
    return pwd_context.hash(password)
```

**What pwd_context does:**
```python
pwd_context = CryptContext(schemes=["bcrypt"])
```

It's a wrapper that:
- Uses bcrypt algorithm
- Handles salt generation automatically
- Provides verify() method

#### 2. JWT Creation:

```python
def create_access_token(data: dict) -> str:
    to_encode = data.copy()  # Don't modify original

    # Add expiration time
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})

    # Sign the token
    encoded_jwt = jwt.encode(
        to_encode,  # Payload (agent_id, scopes)
        settings.secret_key,  # Signing key
        algorithm="HS256"  # HMAC-SHA256
    )
    return encoded_jwt
```

**Token Payload Example:**
```json
{
  "sub": "f02c1a50-f041-4814-91ee-10ae5350a133",  // Agent ID
  "scopes": ["read", "write"],  // Permissions
  "exp": 1737434567  // Expiration timestamp
}
```

**"sub" means "subject"** - standard JWT claim for "who this token is for"

#### 3. Token Verification:

```python
def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=["HS256"]
        )
        return payload
    except JWTError:
        return None  # Invalid token
```

**What can go wrong?**
- Token signature doesn't match (tampered with)
- Token expired
- Token format invalid

---

### 📄 `app/auth/schemas.py`

**Purpose:** Define request/response formats

#### Why separate schemas from database models?

**Database Model** (what's stored):
```python
class Agent(Base):
    hashed_password = Column(String)  # Sensitive!
```

**Response Schema** (what's sent to client):
```python
class AgentResponse(BaseModel):
    # Notice: No hashed_password field!
    id: str
    name: str
    scopes: List[str]
```

**Security principle:** Never expose more data than necessary!

#### Field Validation:

```python
class AgentCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
```

**What this does:**
- `...` means "required field"
- `min_length=3` → Rejects "ab" (too short)
- `min_length=8` → Password must be at least 8 characters

**Custom error messages:**
```python
name: str = Field(
    ...,
    min_length=3,
    description="Agent name (unique identifier)",
    examples=["data-analyzer-agent"]
)
```

This shows up in the API docs!

---

### 📄 `app/auth/dependencies.py`

**Purpose:** Authentication middleware (security guards)

This is where the magic happens! Let me explain in detail:

#### The get_current_agent() Dependency:

```python
async def get_current_agent(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Agent:
```

**What this function does:**

**Step 1:** Extract token from request
```python
# Client sends:
# Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

credentials.credentials  # → "eyJhbGciOiJIUzI1NiIs..."
```

**Step 2:** Decode and validate token
```python
payload = decode_access_token(token)
# payload = {"sub": "agent-id", "scopes": [...], "exp": 123456}
```

**Step 3:** Extract agent ID
```python
agent_id = payload.get("sub")  # "f02c1a50-f041..."
```

**Step 4:** Load agent from database
```python
agent = db.query(Agent).filter(Agent.id == agent_id).first()
```

**Step 5:** Check if agent is active
```python
if not agent.is_active:
    raise HTTPException(403, "Agent deactivated")
```

**Step 6:** Return the agent
```python
return agent  # Now the route handler has the authenticated agent!
```

#### Using the Dependency:

```python
@router.get("/protected")
async def protected_route(
    current_agent: Agent = Depends(get_current_agent)
):
    # current_agent is automatically populated!
    # If token is invalid, this function is never called
    # Instead, HTTPException 401 is raised

    return {"message": f"Hello {current_agent.name}!"}
```

**Execution flow:**
1. Request arrives
2. FastAPI sees `Depends(get_current_agent)`
3. Calls get_current_agent()
4. If it returns an Agent → continue to route handler
5. If it raises HTTPException → return error, skip route handler

---

### 📄 `app/auth/routes.py`

**Purpose:** API endpoints for authentication

#### Understanding Route Decorators:

```python
@router.post("/register", response_model=AgentResponse, status_code=201)
async def register_agent(agent_data: AgentCreate, db: Session = Depends(get_db)):
```

**Breaking this down:**

- `@router.post` → This handles POST requests
- `"/register"` → At the path /auth/register (prefix from router)
- `response_model=AgentResponse` → FastAPI validates response matches this schema
- `status_code=201` → HTTP 201 Created (successful creation)
- `agent_data: AgentCreate` → FastAPI validates request body matches this schema
- `db: Session = Depends(get_db)` → Inject a database session

#### Registration Flow:

```python
# 1. Check if name already exists
existing_agent = db.query(Agent).filter(Agent.name == agent_data.name).first()
if existing_agent:
    raise HTTPException(400, "Agent already exists")

# 2. Hash the password
hashed_password = hash_password(agent_data.password)

# 3. Create agent in database
new_agent = Agent(
    name=agent_data.name,
    hashed_password=hashed_password,
    scopes=agent_data.scopes
)
db.add(new_agent)
db.commit()

# 4. Return agent info (without password!)
return new_agent  # FastAPI converts this to AgentResponse
```

#### Login Flow:

```python
# 1. Find agent by name
agent = db.query(Agent).filter(Agent.name == login_data.name).first()

# 2. Verify password
if not agent or not verify_password(login_data.password, agent.hashed_password):
    raise HTTPException(401, "Incorrect credentials")

# 3. Check if active
if not agent.is_active:
    raise HTTPException(403, "Agent deactivated")

# 4. Update last login
agent.last_login = datetime.utcnow()
db.commit()

# 5. Create JWT token
access_token = create_access_token(
    data={"sub": agent.id, "scopes": agent.scopes}
)

# 6. Return token
return {"access_token": access_token, "token_type": "bearer"}
```

---

## How Authentication Works (Complete Example)

### Scenario: Agent Registration → Login → Access Protected Endpoint

#### Step 1: Agent Registration

**Client Request:**
```http
POST /auth/register HTTP/1.1
Content-Type: application/json

{
  "name": "analyzer-bot",
  "password": "SecurePass123",
  "scopes": ["read", "write"]
}
```

**Server Side:**
1. FastAPI receives request
2. Validates JSON against `AgentCreate` schema
3. Calls `register_agent()` function
4. Hashes password: `"SecurePass123"` → `"$2b$12$KIX..."`
5. Creates database record:
   ```sql
   INSERT INTO agents (id, name, hashed_password, scopes, is_active, created_at)
   VALUES ('uuid', 'analyzer-bot', '$2b$12$KIX...', '["read","write"]', true, '2024-01-27...')
   ```
6. Returns response (without password)

**Client Response:**
```json
{
  "id": "f02c1a50-f041-4814-91ee-10ae5350a133",
  "name": "analyzer-bot",
  "scopes": ["read", "write"],
  "is_active": true,
  "created_at": "2024-01-27T04:49:12.355347"
}
```

---

#### Step 2: Agent Login

**Client Request:**
```http
POST /auth/login HTTP/1.1
Content-Type: application/json

{
  "name": "analyzer-bot",
  "password": "SecurePass123"
}
```

**Server Side:**
1. Looks up agent by name in database
2. Retrieves stored hash: `"$2b$12$KIX..."`
3. Hashes provided password with same salt
4. Compares hashes → Match! ✓
5. Creates JWT:
   ```json
   {
     "sub": "f02c1a50-f041-4814-91ee-10ae5350a133",
     "scopes": ["read", "write"],
     "exp": 1737434567
   }
   ```
6. Signs JWT with SECRET_KEY
7. Updates `last_login` timestamp in database

**Client Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Client stores this token** (in memory, localStorage, etc.)

---

#### Step 3: Accessing Protected Endpoint

**Client Request:**
```http
GET /auth/me HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Server Side:**

1. **Middleware (get_current_agent) runs:**
   - Extracts token from `Authorization` header
   - Decodes JWT: `{"sub": "f02c1a50-...", "scopes": [...], "exp": 123456}`
   - Checks expiration: `datetime.now() < exp` ✓
   - Queries database for agent with ID from "sub"
   - Checks `is_active = True` ✓
   - Returns Agent object

2. **Route handler runs:**
   ```python
   async def get_current_agent_info(current_agent: Agent = Depends(get_current_agent)):
       return current_agent  # Already authenticated!
   ```

**Client Response:**
```json
{
  "id": "f02c1a50-f041-4814-91ee-10ae5350a133",
  "name": "analyzer-bot",
  "scopes": ["read", "write"],
  "is_active": true,
  "created_at": "2024-01-27T04:49:12.355347",
  "last_login": "2024-01-27T05:12:34.567890"
}
```

---

## Security Deep Dive

### Attack Scenarios & Our Defenses

#### 1. **Password Stolen from Database**

**Attack:** Hacker gets database dump
**Defense:** Passwords are bcrypt hashed
**Result:** Hacker has `"$2b$12$KIX..."` but can't reverse it to get original password

**Why cracking is hard:**
- bcrypt is slow (~100ms per hash)
- To try 1 million passwords = 100,000 seconds = 27 hours
- To try 1 billion passwords = 31 years!
- Each password has unique salt

---

#### 2. **JWT Token Intercepted**

**Attack:** Hacker intercepts network traffic, steals token
**Defense:** Multiple layers:
1. Use HTTPS in production (encrypts network traffic)
2. Token expires after 30 minutes
3. Can revoke agent (set `is_active = False`)

**What hacker CAN'T do:**
- Modify token (signature won't match)
- Create new tokens (needs SECRET_KEY)
- Use token after expiration

---

#### 3. **Secret Key Stolen**

**Attack:** Hacker gets SECRET_KEY from .env file
**Defense:**
- `.env` never committed to Git
- Use environment variables in production
- Rotate keys regularly

**If this happens:** Attacker can create valid tokens for any agent!
**Solution:** Immediately rotate SECRET_KEY (invalidates all existing tokens)

---

#### 4. **SQL Injection**

**Attack:** Malicious input like `name = "admin' OR '1'='1"`
**Defense:** SQLAlchemy uses parameterized queries

**What happens:**
```python
# VULNERABLE (raw SQL):
query = f"SELECT * FROM agents WHERE name = '{name}'"
# With name = "admin' OR '1'='1", becomes:
# SELECT * FROM agents WHERE name = 'admin' OR '1'='1'  → Returns all agents!

# SAFE (SQLAlchemy):
db.query(Agent).filter(Agent.name == name).first()
# SQLAlchemy generates:
# SELECT * FROM agents WHERE name = ? with parameter: "admin' OR '1'='1"
# Treats the whole thing as a literal string!
```

---

## Common Questions

### Q: Why not just use cookies for authentication?

**A:** Cookies work for browser-based apps, but:
- AI agents aren't browsers
- APIs need to work with any client (mobile, CLI, other servers)
- JWTs are stateless (no server-side sessions)
- Easier to integrate with microservices

---

### Q: What's the difference between authentication and authorization?

**Authentication:** "Who are you?"
- Proving identity (username + password)
- Getting a token

**Authorization:** "What can you do?"
- Checking permissions (scopes)
- Allowing/denying actions

**Example:**
- Authentication: "You are agent-123" ✓
- Authorization: "You have 'read' scope, so you can view documents" ✓
- Authorization: "You don't have 'delete' scope, so you can't delete documents" ✗

---

### Q: Why do we need both database models AND Pydantic schemas?

**Database Model (SQLAlchemy):**
- How data is STORED
- Includes sensitive fields (hashed_password)
- Has database-specific features (indexes, relationships)

**Pydantic Schema:**
- How data is TRANSMITTED (API requests/responses)
- Excludes sensitive fields
- Has validation rules
- Multiple schemas for same model (CreateSchema, ResponseSchema, UpdateSchema)

**Example:**
```python
# Database: Store everything
class Agent(Base):
    id, name, hashed_password, scopes, is_active, created_at, last_login

# API Response: Only safe data
class AgentResponse(BaseModel):
    id, name, scopes, is_active, created_at, last_login
    # No hashed_password!

# API Request: Different fields
class AgentCreate(BaseModel):
    name, password, scopes  # password (not hashed_password)
    # No id (generated by database)
```

---

### Q: What happens if two agents register with the same name?

**A:** Database constraint prevents it:
```python
name = Column(String, unique=True)
```

**Flow:**
1. Second agent tries to register
2. SQLAlchemy tries: `INSERT INTO agents (name, ...) VALUES ('agent-1', ...)`
3. Database raises: `IntegrityError: UNIQUE constraint failed: agents.name`
4. Our code catches this and returns:
   ```python
   raise HTTPException(400, "Agent with name 'agent-1' already exists")
   ```

---

### Q: Can I use the same password for multiple agents?

**A:** Yes! Even though hashes will be different (due to salt).

**Example:**
```
Agent 1: password="test123" → hash="$2b$12$abc..."
Agent 2: password="test123" → hash="$2b$12$xyz..."  // Different!
```

Each call to bcrypt generates a new salt, so hashes are unique.

---

## Next Steps

Now that you understand the foundation, you're ready to build:

1. **Advanced Permission System**
   - Role-based access control (RBAC)
   - Scope validation in routes
   - Admin vs. regular agents

2. **RAG Pipeline**
   - Vector databases (FAISS)
   - Document embeddings
   - Access-controlled knowledge base

3. **Audit Logging**
   - Track every agent action
   - Timestamps, IP addresses
   - Compliance and security

4. **Production Deployment**
   - Docker containers
   - PostgreSQL database
   - HTTPS with TLS certificates
   - Environment-based configs

---

## Exercises to Test Your Understanding

Try these challenges:

1. **Add email field to agents** (Update model, schema, and route)
2. **Implement password change endpoint** (Verify old password, hash new one)
3. **Add "admin" scope** (Create a dependency that checks for admin scope)
4. **Token refresh endpoint** (Issue new token without re-login)
5. **Rate limiting** (Prevent brute-force login attempts)

When you're ready, we can tackle these together!

---

**Questions?** Ask about ANY concept - I want to make sure you understand everything deeply!

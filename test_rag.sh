#!/bin/bash
# Test script for RAG (Retrieval Augmented Generation) system

BASE_URL="http://localhost:8001"

echo "=========================================="
echo "  RAG System Demo"
echo "=========================================="
echo

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "Step 1: Create an agent with read/write scopes..."
echo "--------------------------------------------"
curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "doc-manager",
    "password": "Test123!",
    "scopes": ["read", "write"],
    "description": "Agent for managing documents"
  }' | python3 -m json.tool
echo
echo

echo "Step 2: Login and get token..."
echo "--------------------------------------------"
TOKEN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"name": "doc-manager", "password": "Test123!"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo -e "${GREEN}✓ Token obtained${NC}"
echo
echo

echo "Step 3: Upload documents..."
echo "--------------------------------------------"

echo -e "${BLUE}Uploading document about JWT authentication...${NC}"
curl -s -X POST "$BASE_URL/rag/documents" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "JWT (JSON Web Token) is a compact, URL-safe means of representing claims to be transferred between two parties. The claims in a JWT are encoded as a JSON object that is used as the payload of a JSON Web Signature (JWS) structure or as the plaintext of a JSON Web Encryption (JWE) structure. This enables the claims to be digitally signed or integrity protected with a Message Authentication Code (MAC) and/or encrypted. JWTs consist of three parts: header, payload, and signature. The header typically consists of two parts: the type of token (JWT) and the signing algorithm (HS256, RS256, etc.). The payload contains the claims, which are statements about an entity and additional data. The signature is used to verify the sender and ensure the message was not changed.",
    "filename": "jwt_guide.txt",
    "file_type": "txt",
    "allowed_scopes": ["read"]
  }' | python3 -m json.tool
echo
echo

echo -e "${BLUE}Uploading document about Python FastAPI...${NC}"
curl -s -X POST "$BASE_URL/rag/documents" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "FastAPI is a modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints. The key features are: Fast, very high performance on par with NodeJS and Go. Fast to code, increase the speed to develop features. Fewer bugs, reduce about 40% of human induced errors. Intuitive, great editor support with completion everywhere. Easy to use and learn. FastAPI is based on Pydantic for data validation and Starlette for the web parts. It provides automatic interactive API documentation using Swagger UI and ReDoc. FastAPI supports async/await for concurrent request handling, making it extremely efficient for I/O-bound operations.",
    "filename": "fastapi_intro.txt",
    "file_type": "txt",
    "allowed_scopes": ["read"]
  }' | python3 -m json.tool
echo
echo

echo -e "${BLUE}Uploading document about Vector Databases...${NC}"
curl -s -X POST "$BASE_URL/rag/documents" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Vector databases are specialized databases designed to store and query high-dimensional vectors efficiently. They are essential for AI applications like semantic search, recommendation systems, and retrieval augmented generation (RAG). FAISS (Facebook AI Similarity Search) is a library that provides efficient similarity search and clustering of dense vectors. It supports billion-scale datasets and includes GPU implementations for faster processing. Vector databases use various indexing techniques like IVF (Inverted File Index), HNSW (Hierarchical Navigable Small World), and Product Quantization to enable fast approximate nearest neighbor search. The key metric is similarity, often measured using cosine similarity or L2 distance.",
    "filename": "vector_databases.txt",
    "file_type": "txt",
    "allowed_scopes": ["read", "write"]
  }' | python3 -m json.tool
echo
echo

echo "Step 4: List all documents..."
echo "--------------------------------------------"
curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/rag/documents" | python3 -m json.tool
echo
echo

echo "Step 5: Query documents with semantic search..."
echo "--------------------------------------------"

echo -e "${YELLOW}Query 1: \"How do I build APIs in Python?\"${NC}"
curl -s -X POST "$BASE_URL/rag/query" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I build APIs in Python?",
    "top_k": 2
  }' | python3 -m json.tool
echo
echo

echo -e "${YELLOW}Query 2: \"What is token-based authentication?\"${NC}"
curl -s -X POST "$BASE_URL/rag/query" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is token-based authentication?",
    "top_k": 2
  }' | python3 -m json.tool
echo
echo

echo -e "${YELLOW}Query 3: \"How does similarity search work?\"${NC}"
curl -s -X POST "$BASE_URL/rag/query" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How does similarity search work?",
    "top_k": 2
  }' | python3 -m json.tool
echo
echo

echo "Step 6: Get RAG system statistics..."
echo "--------------------------------------------"
curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/rag/stats" | python3 -m json.tool
echo
echo

echo "=========================================="
echo "  Summary"
echo "=========================================="
echo
echo "This demo showed:"
echo "  ✓ Document upload with access control"
echo "  ✓ Text chunking and embedding generation"
echo "  ✓ Vector storage in FAISS"
echo "  ✓ Semantic search (finds meaning, not just keywords)"
echo "  ✓ Permission-based document access"
echo
echo "Key Concepts:"
echo "  - Embeddings: Text converted to vectors (numbers)"
echo "  - Semantic Search: Find similar meaning, not exact matches"
echo "  - RAG: Retrieve relevant info to augment AI responses"
echo "  - Access Control: Only show documents agent can access"
echo
echo "=========================================="
echo "  Test Complete!"
echo "=========================================="

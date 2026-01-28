#!/bin/bash
# Test script for scope-based authorization

BASE_URL="http://localhost:8001"

echo "=========================================="
echo "  Scope-Based Authorization Demo"
echo "=========================================="
echo

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Step 1: Creating agents with different scopes..."
echo "--------------------------------------------"

echo -e "${YELLOW}Creating 'reader-agent' with only [read] scope...${NC}"
curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "reader-agent",
    "password": "Test123!",
    "scopes": ["read"],
    "description": "Agent with read-only access"
  }' | python3 -m json.tool
echo
echo

echo -e "${YELLOW}Creating 'writer-agent' with [read, write] scopes...${NC}"
curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "writer-agent",
    "password": "Test123!",
    "scopes": ["read", "write"],
    "description": "Agent with read and write access"
  }' | python3 -m json.tool
echo
echo

echo -e "${YELLOW}Creating 'admin-agent' with [read, write, admin] scopes...${NC}"
curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "admin-agent",
    "password": "Test123!",
    "scopes": ["read", "write", "admin"],
    "description": "Agent with full administrative access"
  }' | python3 -m json.tool
echo
echo

echo "=========================================="
echo "Step 2: Testing endpoints with different scope requirements"
echo "=========================================="
echo

# Get tokens for each agent
echo "Getting access tokens..."
READER_TOKEN=$(curl -s -X POST "$BASE_URL/auth/login" -H "Content-Type: application/json" -d '{"name": "reader-agent", "password": "Test123!"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
WRITER_TOKEN=$(curl -s -X POST "$BASE_URL/auth/login" -H "Content-Type: application/json" -d '{"name": "writer-agent", "password": "Test123!"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
ADMIN_TOKEN=$(curl -s -X POST "$BASE_URL/auth/login" -H "Content-Type: application/json" -d '{"name": "admin-agent", "password": "Test123!"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo "✓ Tokens obtained"
echo
echo

# Test 1: Read-only endpoint (all should succeed)
echo "--------------------------------------------"
echo -e "${YELLOW}Test 1: /demo/read-only (No scope requirement)${NC}"
echo "--------------------------------------------"

echo -e "${GREEN}Reader agent (should succeed):${NC}"
curl -s -H "Authorization: Bearer $READER_TOKEN" "$BASE_URL/auth/demo/read-only" | python3 -m json.tool
echo
echo

echo -e "${GREEN}Writer agent (should succeed):${NC}"
curl -s -H "Authorization: Bearer $WRITER_TOKEN" "$BASE_URL/auth/demo/read-only" | python3 -m json.tool
echo
echo


# Test 2: Write-protected endpoint
echo "--------------------------------------------"
echo -e "${YELLOW}Test 2: /demo/write-protected (Requires 'write' scope)${NC}"
echo "--------------------------------------------"

echo -e "${RED}Reader agent (should FAIL - missing 'write'):${NC}"
curl -s -H "Authorization: Bearer $READER_TOKEN" "$BASE_URL/auth/demo/write-protected"
echo
echo

echo -e "${GREEN}Writer agent (should succeed):${NC}"
curl -s -H "Authorization: Bearer $WRITER_TOKEN" "$BASE_URL/auth/demo/write-protected" | python3 -m json.tool
echo
echo


# Test 3: Admin-only endpoint
echo "--------------------------------------------"
echo -e "${YELLOW}Test 3: /demo/admin-only (Requires 'admin' scope)${NC}"
echo "--------------------------------------------"

echo -e "${RED}Reader agent (should FAIL - missing 'admin'):${NC}"
curl -s -H "Authorization: Bearer $READER_TOKEN" "$BASE_URL/auth/demo/admin-only"
echo
echo

echo -e "${RED}Writer agent (should FAIL - missing 'admin'):${NC}"
curl -s -H "Authorization: Bearer $WRITER_TOKEN" "$BASE_URL/auth/demo/admin-only"
echo
echo

echo -e "${GREEN}Admin agent (should succeed):${NC}"
curl -s -H "Authorization: Bearer $ADMIN_TOKEN" "$BASE_URL/auth/demo/admin-only" | python3 -m json.tool
echo
echo


# Test 4: Multi-scope requirement
echo "--------------------------------------------"
echo -e "${YELLOW}Test 4: /demo/multi-scope (Requires BOTH 'read' AND 'write')${NC}"
echo "--------------------------------------------"

echo -e "${RED}Reader agent (should FAIL - missing 'write'):${NC}"
curl -s -H "Authorization: Bearer $READER_TOKEN" "$BASE_URL/auth/demo/multi-scope"
echo
echo

echo -e "${GREEN}Writer agent (should succeed):${NC}"
curl -s -H "Authorization: Bearer $WRITER_TOKEN" "$BASE_URL/auth/demo/multi-scope" | python3 -m json.tool
echo
echo


# Test 5: No authentication
echo "--------------------------------------------"
echo -e "${YELLOW}Test 5: Accessing without token (should FAIL)${NC}"
echo "--------------------------------------------"

echo -e "${RED}No token provided:${NC}"
curl -s "$BASE_URL/auth/demo/read-only"
echo
echo
echo

echo "=========================================="
echo "  Summary"
echo "=========================================="
echo
echo "This demo showed:"
echo "  ✓ Different agents with different scopes"
echo "  ✓ Endpoints with no scope requirements (just auth)"
echo "  ✓ Endpoints requiring specific scopes ('write', 'admin')"
echo "  ✓ Endpoints requiring multiple scopes"
echo "  ✓ Automatic 403 Forbidden when scopes are missing"
echo
echo "Key Concepts:"
echo "  - Authentication: Proving WHO you are (valid token)"
echo "  - Authorization: Checking WHAT you can do (scopes)"
echo "  - Scopes: Permissions that control access to endpoints"
echo
echo "=========================================="
echo "  Test Complete!"
echo "=========================================="

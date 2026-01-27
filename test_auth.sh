#!/bin/bash
# Test script for AI Agent Identity Gateway Authentication

BASE_URL="http://localhost:8001"

echo "=== AI Agent Identity Gateway - Authentication Test ==="
echo

echo "1. Registering a new agent..."
curl -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "demo-agent",
    "password": "SecurePass123!",
    "scopes": ["read", "write", "execute"],
    "description": "Demo agent for testing"
  }' | python3 -m json.tool
echo
echo

echo "2. Logging in to get access token..."
TOKEN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "demo-agent",
    "password": "SecurePass123!"
  }' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo "Token received: ${TOKEN:0:50}..."
echo
echo

echo "3. Testing protected endpoint with token..."
curl -H "Authorization: Bearer $TOKEN" "$BASE_URL/auth/me" | python3 -m json.tool
echo
echo

echo "4. Testing without token (should fail)..."
curl -s "$BASE_URL/auth/me"
echo
echo

echo "=== Test Complete ==="

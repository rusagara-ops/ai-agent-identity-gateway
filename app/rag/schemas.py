"""
Pydantic schemas for RAG endpoints.

Defines the shape of data for document upload, query, and responses.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class DocumentUpload(BaseModel):
    """Schema for document upload request."""
    content: str = Field(..., description="Text content of the document")
    filename: str = Field(..., min_length=1, description="Name of the file")
    file_type: str = Field(default="txt", description="File type (txt, pdf, etc.)")
    allowed_scopes: List[str] = Field(default=["read"], description="Scopes that can access this document")

    class Config:
        json_schema_extra = {
            "example": {
                "content": "This is the content of my document about AI security...",
                "filename": "ai_security_guide.txt",
                "file_type": "txt",
                "allowed_scopes": ["read", "write"]
            }
        }


class DocumentResponse(BaseModel):
    """Schema for document information in responses."""
    id: str
    filename: str
    file_type: str
    owner_id: str
    allowed_scopes: List[str]
    created_at: datetime
    size_bytes: Optional[int]

    class Config:
        from_attributes = True


class QueryRequest(BaseModel):
    """Schema for RAG query request."""
    query: str = Field(..., min_length=1, description="The query to search for")
    top_k: int = Field(default=3, ge=1, le=10, description="Number of results to return")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "How does JWT authentication work?",
                "top_k": 3
            }
        }


class QueryResult(BaseModel):
    """Schema for a single search result."""
    document_id: str
    filename: str
    content: str
    similarity_score: float
    chunk_index: int


class QueryResponse(BaseModel):
    """Schema for query response."""
    query: str
    results: List[QueryResult]
    total_results: int

    class Config:
        json_schema_extra = {
            "example": {
                "query": "How does JWT authentication work?",
                "results": [
                    {
                        "document_id": "doc-123",
                        "filename": "auth_guide.txt",
                        "content": "JWT tokens are signed JSON objects...",
                        "similarity_score": 0.95,
                        "chunk_index": 0
                    }
                ],
                "total_results": 3
            }
        }

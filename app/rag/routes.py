"""
RAG API routes for document management and semantic search.

Endpoints:
- POST /rag/documents - Upload a document
- GET /rag/documents - List accessible documents
- POST /rag/query - Query documents with semantic search
- DELETE /rag/documents/{doc_id} - Delete a document
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.models import Agent, Document, get_db
from app.auth.dependencies import get_current_agent, require_scopes
from app.rag.schemas import DocumentUpload, DocumentResponse, QueryRequest, QueryResponse, QueryResult
from app.rag.embeddings import generate_embeddings, chunk_text
from app.rag.vectorstore import get_vector_store

# Create router with /rag prefix
router = APIRouter(prefix="/rag", tags=["RAG Pipeline"])


@router.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    doc_data: DocumentUpload,
    current_agent: Agent = Depends(require_scopes(["write"])),
    db: Session = Depends(get_db)
):
    """
    Upload a document to the RAG system.

    This endpoint:
    1. Requires 'write' scope
    2. Chunks the document into smaller pieces
    3. Generates embeddings for each chunk
    4. Stores vectors in FAISS
    5. Saves document metadata in database

    Args:
        doc_data: Document content and metadata
        current_agent: Currently authenticated agent (must have 'write' scope)
        db: Database session

    Returns:
        DocumentResponse: Created document information
    """
    # Chunk the text
    chunks = chunk_text(doc_data.content, chunk_size=500, overlap=50)

    # Generate embeddings
    embeddings = generate_embeddings(chunks)

    # Create document record
    new_doc = Document(
        filename=doc_data.filename,
        content=doc_data.content,
        file_type=doc_data.file_type,
        owner_id=current_agent.id,
        allowed_scopes=doc_data.allowed_scopes,
        size_bytes=len(doc_data.content)
    )

    db.add(new_doc)
    db.flush()  # Get the ID without committing

    # Add vectors to FAISS
    vector_store = get_vector_store()
    vector_ids = vector_store.add_vectors(
        embeddings,
        new_doc.id,
        new_doc.filename,
        chunks
    )

    # Store vector IDs in document
    new_doc.vector_ids = vector_ids

    db.commit()
    db.refresh(new_doc)

    return new_doc


@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(
    current_agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """
    List all documents accessible to the current agent.

    Access control:
    - Agents can see their own documents
    - Agents can see documents where their scopes overlap with allowed_scopes

    Args:
        current_agent: Currently authenticated agent
        db: Database session

    Returns:
        List[DocumentResponse]: List of accessible documents
    """
    # Get agent's scopes
    agent_scopes = set(current_agent.scopes or [])

    # Query all documents
    all_docs = db.query(Document).all()

    # Filter based on access control
    accessible_docs = []
    for doc in all_docs:
        # Agent owns the document
        if doc.owner_id == current_agent.id:
            accessible_docs.append(doc)
            continue

        # Agent has at least one of the allowed scopes
        doc_scopes = set(doc.allowed_scopes or [])
        if agent_scopes & doc_scopes:  # Intersection
            accessible_docs.append(doc)

    return accessible_docs


@router.post("/query", response_model=QueryResponse)
async def query_documents(
    query_data: QueryRequest,
    current_agent: Agent = Depends(require_scopes(["read"])),
    db: Session = Depends(get_db)
):
    """
    Query documents using semantic search.

    This endpoint:
    1. Requires 'read' scope
    2. Generates embedding for the query
    3. Searches FAISS for similar vectors
    4. Filters results based on access control
    5. Returns relevant document chunks

    Args:
        query_data: Query text and parameters
        current_agent: Currently authenticated agent (must have 'read' scope)
        db: Database session

    Returns:
        QueryResponse: Search results with similarity scores
    """
    # Get accessible document IDs
    agent_scopes = set(current_agent.scopes or [])
    all_docs = db.query(Document).all()

    allowed_doc_ids = []
    for doc in all_docs:
        if doc.owner_id == current_agent.id:
            allowed_doc_ids.append(doc.id)
        else:
            doc_scopes = set(doc.allowed_scopes or [])
            if agent_scopes & doc_scopes:
                allowed_doc_ids.append(doc.id)

    if not allowed_doc_ids:
        return QueryResponse(
            query=query_data.query,
            results=[],
            total_results=0
        )

    # Generate query embedding
    query_embedding = generate_embeddings([query_data.query])[0]

    # Search vector store
    vector_store = get_vector_store()
    search_results = vector_store.search(
        query_embedding,
        top_k=query_data.top_k,
        allowed_document_ids=allowed_doc_ids
    )

    # Format results
    results = []
    for meta, score in search_results:
        results.append(QueryResult(
            document_id=meta["document_id"],
            filename=meta["filename"],
            content=meta["chunk_text"],
            similarity_score=score,
            chunk_index=meta["chunk_index"]
        ))

    return QueryResponse(
        query=query_data.query,
        results=results,
        total_results=len(results)
    )


@router.delete("/documents/{document_id}", status_code=status.HTTP_200_OK)
async def delete_document(
    document_id: str,
    current_agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """
    Delete a document.

    Only the owner can delete their documents.

    Args:
        document_id: ID of document to delete
        current_agent: Currently authenticated agent
        db: Database session

    Returns:
        dict: Success message
    """
    # Find document
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' not found"
        )

    # Check ownership
    if document.owner_id != current_agent.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own documents"
        )

    # Delete from vector store
    vector_store = get_vector_store()
    vector_store.delete_document_vectors(document_id)

    # Delete from database
    db.delete(document)
    db.commit()

    return {"message": f"Document '{document.filename}' deleted successfully"}


@router.get("/stats")
async def get_rag_stats(
    current_agent: Agent = Depends(get_current_agent)
):
    """
    Get RAG system statistics.

    Returns:
        dict: Stats about vector store and documents
    """
    vector_store = get_vector_store()
    return {
        **vector_store.get_stats(),
        "agent_id": current_agent.id,
        "agent_scopes": current_agent.scopes
    }

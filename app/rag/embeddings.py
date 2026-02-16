"""
Embedding generation for RAG system.

Converts text into vector representations for semantic search.
Uses sentence-transformers for local embeddings (no API key needed).
"""

from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

# Global model instance (loaded once at startup)
_model = None


def get_embedding_model():
    """
    Get or create the embedding model.

    Uses sentence-transformers with 'all-MiniLM-L6-v2' model:
    - 384-dimensional embeddings
    - Fast inference
    - Good quality for semantic search
    - Runs locally (no API calls)

    Returns:
        SentenceTransformer: The embedding model
    """
    global _model
    if _model is None:
        print("Loading embedding model (first time only)...")
        _model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✓ Embedding model loaded")
    return _model


def generate_embeddings(texts: List[str]) -> np.ndarray:
    """
    Generate embeddings for a list of texts.

    Args:
        texts: List of text strings to embed

    Returns:
        np.ndarray: Array of embeddings, shape (len(texts), embedding_dim)
    """
    model = get_embedding_model()
    embeddings = model.encode(texts, show_progress_bar=False)
    return embeddings


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks for better retrieval.

    Why chunking?
    - Documents can be too long for a single embedding
    - Smaller chunks = more precise retrieval
    - Overlap ensures context isn't lost at boundaries

    Args:
        text: The text to chunk
        chunk_size: Target size of each chunk (in characters)
        overlap: Number of characters to overlap between chunks

    Returns:
        List[str]: List of text chunks

    Example:
        text = "This is a long document about AI. It has many sections..."
        chunks = chunk_text(text, chunk_size=100, overlap=20)
        # chunks[0] = "This is a long document about AI. It has"
        # chunks[1] = "about AI. It has many sections and explains..."
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())

        # Move start forward by (chunk_size - overlap)
        start += (chunk_size - overlap)

        # Stop if we've reached the end
        if end >= len(text):
            break

    return [c for c in chunks if c]  # Filter out empty chunks

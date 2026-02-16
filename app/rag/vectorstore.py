"""
FAISS vector store for similarity search.

FAISS (Facebook AI Similarity Search) is a library for efficient similarity search.
It stores vectors and finds the most similar ones quickly.
"""

import faiss
import numpy as np
import pickle
import os
from typing import List, Tuple, Dict
from pathlib import Path

from app.config import settings


class VectorStore:
    """
    Manages FAISS index for document embeddings.

    Key Concepts:
    - Index: Data structure that stores vectors
    - L2 Distance: Euclidean distance between vectors (lower = more similar)
    - Metadata: Additional info about each vector (document ID, chunk index, etc.)
    """

    def __init__(self, embedding_dim: int = 384):
        """
        Initialize the vector store.

        Args:
            embedding_dim: Dimension of embeddings (384 for all-MiniLM-L6-v2)
        """
        self.embedding_dim = embedding_dim
        self.index = faiss.IndexFlatL2(embedding_dim)  # L2 distance (Euclidean)
        self.metadata = []  # Store document_id, chunk_index, etc.
        self.index_file = Path(settings.faiss_index_path + ".index")
        self.metadata_file = Path(settings.faiss_index_path + ".metadata")

        # Create directory if it doesn't exist
        self.index_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing index if available
        self.load()

    def add_vectors(
        self,
        embeddings: np.ndarray,
        document_id: str,
        filename: str,
        chunks: List[str]
    ) -> List[int]:
        """
        Add vectors to the index with metadata.

        Args:
            embeddings: Array of embeddings, shape (n_chunks, embedding_dim)
            document_id: ID of the document
            filename: Name of the document
            chunks: Original text chunks

        Returns:
            List[int]: FAISS vector IDs for the added vectors
        """
        # Get starting index
        start_idx = self.index.ntotal

        # Add vectors to FAISS index
        self.index.add(embeddings.astype('float32'))

        # Store metadata for each vector
        vector_ids = []
        for i, chunk in enumerate(chunks):
            vector_id = start_idx + i
            vector_ids.append(vector_id)

            self.metadata.append({
                "vector_id": vector_id,
                "document_id": document_id,
                "filename": filename,
                "chunk_index": i,
                "chunk_text": chunk
            })

        # Save to disk
        self.save()

        return vector_ids

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 3,
        allowed_document_ids: List[str] = None
    ) -> List[Tuple[Dict, float]]:
        """
        Search for similar vectors.

        Args:
            query_embedding: Query vector, shape (1, embedding_dim)
            top_k: Number of results to return
            allowed_document_ids: Filter results to these document IDs (for access control)

        Returns:
            List of tuples: (metadata_dict, similarity_score)
        """
        if self.index.ntotal == 0:
            return []

        # Search FAISS index
        # distances: L2 distances (lower = more similar)
        # indices: Vector IDs of nearest neighbors
        distances, indices = self.index.search(
            query_embedding.astype('float32').reshape(1, -1),
            min(top_k * 3, self.index.ntotal)  # Get extra results for filtering
        )

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            # Get metadata for this vector
            if idx < len(self.metadata):
                meta = self.metadata[idx]

                # Apply access control filter
                if allowed_document_ids and meta["document_id"] not in allowed_document_ids:
                    continue

                # Convert L2 distance to similarity score (0-1 range)
                # Lower distance = higher similarity
                similarity = 1.0 / (1.0 + float(dist))

                results.append((meta, similarity))

                if len(results) >= top_k:
                    break

        return results

    def delete_document_vectors(self, document_id: str):
        """
        Delete all vectors for a document.

        Note: FAISS doesn't support deletion, so we rebuild the index.

        Args:
            document_id: ID of document to delete
        """
        # Filter out metadata for this document
        new_metadata = [m for m in self.metadata if m["document_id"] != document_id]

        if len(new_metadata) == len(self.metadata):
            # No vectors to delete
            return

        # Rebuild index without deleted vectors
        self.index = faiss.IndexFlatL2(self.embedding_dim)

        # Re-add all other vectors
        if new_metadata:
            # Collect embeddings (we'd need to store these - for now just clear)
            # In production, you'd re-embed or store embeddings
            pass

        self.metadata = new_metadata
        self.save()

    def save(self):
        """Save index and metadata to disk."""
        # Save FAISS index
        faiss.write_index(self.index, str(self.index_file))

        # Save metadata
        with open(self.metadata_file, 'wb') as f:
            pickle.dump(self.metadata, f)

    def load(self):
        """Load index and metadata from disk."""
        if self.index_file.exists() and self.metadata_file.exists():
            try:
                # Load FAISS index
                self.index = faiss.read_index(str(self.index_file))

                # Load metadata
                with open(self.metadata_file, 'rb') as f:
                    self.metadata = pickle.load(f)

                print(f"✓ Loaded {self.index.ntotal} vectors from disk")
            except Exception as e:
                print(f"Warning: Could not load index: {e}")
                # Start fresh
                self.index = faiss.IndexFlatL2(self.embedding_dim)
                self.metadata = []

    def get_stats(self) -> Dict:
        """Get statistics about the vector store."""
        return {
            "total_vectors": self.index.ntotal,
            "embedding_dim": self.embedding_dim,
            "unique_documents": len(set(m["document_id"] for m in self.metadata)),
            "index_file": str(self.index_file),
            "metadata_file": str(self.metadata_file)
        }


# Global vector store instance
_vector_store = None


def get_vector_store() -> VectorStore:
    """
    Get or create the global vector store instance.

    Returns:
        VectorStore: The vector store
    """
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store

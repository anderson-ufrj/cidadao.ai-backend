"""
Module: services.vector_store_service
Description: Vector store service for semantic similarity search
Author: Anderson H. Silva
Date: 2025-10-20
License: Proprietary - All rights reserved
"""

import asyncio
from typing import Any

import chromadb
import structlog
from chromadb.utils import embedding_functions

logger = structlog.get_logger(__name__)


class VectorStoreService:
    """Vector store service using ChromaDB for semantic similarity search."""

    def __init__(
        self,
        collection_name: str = "cidadao_memory",
        persist_directory: str = "./chroma_db",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    ) -> None:
        """
        Initialize vector store service.

        Args:
            collection_name: Name of the collection
            persist_directory: Directory to persist data
            embedding_model: Sentence transformer model for embeddings
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.embedding_model = embedding_model
        self.client: chromadb.Client | None = None
        self.collection: chromadb.Collection | None = None
        self.embedding_function = None

        logger.info(
            "vector_store_initializing",
            collection=collection_name,
            model=embedding_model,
        )

    async def initialize(self) -> None:
        """Initialize ChromaDB client and collection."""
        try:
            # Run synchronous ChromaDB init in thread pool
            await asyncio.to_thread(self._sync_initialize)

            logger.info(
                "vector_store_initialized",
                collection=self.collection_name,
            )
        except Exception as e:
            logger.error(
                "vector_store_initialization_failed",
                error=str(e),
                collection=self.collection_name,
            )
            raise

    def _sync_initialize(self) -> None:
        """Synchronous initialization of ChromaDB."""
        # Create embedding function
        self.embedding_function = (
            embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=self.embedding_model
            )
        )

        # Initialize ChromaDB client with new API (persistent client)
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function,
            metadata={"description": "Cidadão.AI memory storage"},
        )

    async def add_documents(
        self,
        documents: list[dict[str, Any]],
    ) -> None:
        """
        Add documents to vector store.

        Args:
            documents: List of documents with 'id', 'text', and 'metadata'
        """
        if not self.collection:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")

        try:
            # Extract data from documents
            ids = [doc["id"] for doc in documents]
            texts = [doc.get("text", str(doc.get("content", ""))) for doc in documents]
            metadatas = [doc.get("metadata", {}) for doc in documents]

            # Add to collection (sync operation in thread pool)
            await asyncio.to_thread(
                self.collection.add,
                ids=ids,
                documents=texts,
                metadatas=metadatas,
            )

            logger.info(
                "documents_added_to_vector_store",
                count=len(documents),
                collection=self.collection_name,
            )

        except Exception as e:
            logger.error(
                "failed_to_add_documents",
                error=str(e),
                count=len(documents),
                collection=self.collection_name,
            )
            raise

    async def similarity_search(
        self,
        query: str,
        limit: int = 5,
        filter_metadata: dict[str, Any] | None = None,
        similarity_threshold: float = 0.0,
    ) -> list[dict[str, Any]]:
        """
        Search for similar documents.

        Args:
            query: Query text
            limit: Maximum number of results
            filter_metadata: Metadata filters (where clause)
            similarity_threshold: Minimum similarity score (0-1)

        Returns:
            List of similar documents with scores
        """
        if not self.collection:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")

        try:
            # Query collection (sync operation in thread pool)
            results = await asyncio.to_thread(
                self.collection.query,
                query_texts=[query],
                n_results=limit,
                where=filter_metadata,
            )

            # Format results
            documents = []
            if results["ids"] and len(results["ids"]) > 0:
                for i, doc_id in enumerate(results["ids"][0]):
                    # Get distance (lower is better, convert to similarity)
                    distance = (
                        results["distances"][0][i] if "distances" in results else 0.0
                    )
                    similarity = 1.0 - distance  # Convert distance to similarity

                    # Filter by similarity threshold
                    if similarity >= similarity_threshold:
                        documents.append(
                            {
                                "id": doc_id,
                                "text": (
                                    results["documents"][0][i]
                                    if "documents" in results
                                    else ""
                                ),
                                "metadata": (
                                    results["metadatas"][0][i]
                                    if "metadatas" in results
                                    else {}
                                ),
                                "similarity": similarity,
                                "distance": distance,
                            }
                        )

            logger.info(
                "similarity_search_completed",
                query_length=len(query),
                results_count=len(documents),
                limit=limit,
            )

            return documents

        except Exception as e:
            logger.error(
                "similarity_search_failed",
                error=str(e),
                query=query[:100],  # Log only first 100 chars
            )
            raise

    async def delete_documents(
        self,
        ids: list[str],
    ) -> None:
        """
        Delete documents by IDs.

        Args:
            ids: List of document IDs to delete
        """
        if not self.collection:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")

        try:
            # Delete from collection (sync operation in thread pool)
            await asyncio.to_thread(
                self.collection.delete,
                ids=ids,
            )

            logger.info(
                "documents_deleted_from_vector_store",
                count=len(ids),
                collection=self.collection_name,
            )

        except Exception as e:
            logger.error(
                "failed_to_delete_documents",
                error=str(e),
                ids=ids,
            )
            raise

    async def get_document(
        self,
        doc_id: str,
    ) -> dict[str, Any] | None:
        """
        Get a document by ID.

        Args:
            doc_id: Document ID

        Returns:
            Document or None if not found
        """
        if not self.collection:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")

        try:
            # Get from collection (sync operation in thread pool)
            result = await asyncio.to_thread(
                self.collection.get,
                ids=[doc_id],
                include=["documents", "metadatas"],
            )

            if result["ids"] and len(result["ids"]) > 0:
                return {
                    "id": result["ids"][0],
                    "text": result["documents"][0] if "documents" in result else "",
                    "metadata": result["metadatas"][0] if "metadatas" in result else {},
                }

            return None

        except Exception as e:
            logger.error(
                "failed_to_get_document",
                error=str(e),
                doc_id=doc_id,
            )
            raise

    async def count(self) -> int:
        """
        Get total count of documents in collection.

        Returns:
            Number of documents
        """
        if not self.collection:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")

        try:
            # Count (sync operation in thread pool)
            count = await asyncio.to_thread(self.collection.count)

            logger.info(
                "vector_store_count",
                count=count,
                collection=self.collection_name,
            )

            return count

        except Exception as e:
            logger.error(
                "failed_to_count_documents",
                error=str(e),
            )
            raise

    async def close(self) -> None:
        """Close vector store connection."""
        # ChromaDB PersistentClient auto-persists data, no need to manually persist
        if self.client:
            logger.info(
                "vector_store_closed",
                collection=self.collection_name,
            )

        self.client = None
        self.collection = None


class VectorStoreFactory:
    """Factory for managing vector store singleton instance."""

    _instance: VectorStoreService | None = None

    @classmethod
    def get_instance(
        cls,
        collection_name: str = "cidadao_memory",
        persist_directory: str = "./chroma_db",
    ) -> VectorStoreService:
        """
        Get singleton vector store instance.

        Args:
            collection_name: Name of the collection
            persist_directory: Directory to persist data

        Returns:
            Vector store service instance
        """
        if cls._instance is None:
            cls._instance = VectorStoreService(
                collection_name=collection_name,
                persist_directory=persist_directory,
            )

        return cls._instance


# Convenience function
def get_vector_store(
    collection_name: str = "cidadao_memory",
    persist_directory: str = "./chroma_db",
) -> VectorStoreService:
    """Get vector store instance (convenience wrapper)."""
    return VectorStoreFactory.get_instance(collection_name, persist_directory)

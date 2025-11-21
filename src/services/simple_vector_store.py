"""
Simple in-memory vector store for production without chromadb dependency
"""

from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class SimpleVectorStore:
    """Simple in-memory vector store replacement for VectorStoreService."""

    def __init__(
        self,
        collection_name: str = "cidadao_memory",
        persist_directory: str = "./chroma_db",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    ) -> None:
        """Initialize simple in-memory store (ignores parameters for compatibility)."""
        self.store: dict[str, Any] = {}
        self.initialized = False
        # Parameters ignored - kept for interface compatibility
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.embedding_model = embedding_model
        logger.info("simple_vector_store_initialized", mode="in-memory")

    async def initialize(self) -> None:
        """Initialize the store (no-op for in-memory)."""
        self.initialized = True

    async def add_memory(
        self, memory_id: str, content: str, metadata: dict[str, Any]
    ) -> None:
        """Add memory to store."""
        self.store[memory_id] = {"content": content, "metadata": metadata}

    async def search_memories(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Search memories (simple text matching)."""
        results = []
        query_lower = query.lower()

        for memory_id, memory_data in self.store.items():
            content_lower = memory_data["content"].lower()

            # Simple text matching
            if query_lower in content_lower:
                # Apply metadata filter if provided
                if filter_metadata:
                    match = all(
                        memory_data["metadata"].get(k) == v
                        for k, v in filter_metadata.items()
                    )
                    if not match:
                        continue

                results.append(
                    {
                        "id": memory_id,
                        "content": memory_data["content"],
                        "metadata": memory_data["metadata"],
                        "score": 1.0,  # Simple scoring
                    }
                )

        # Return top n_results
        return results[:n_results]

    async def get_memory(self, memory_id: str) -> dict[str, Any] | None:
        """Get specific memory by ID."""
        if memory_id in self.store:
            return {"id": memory_id, **self.store[memory_id]}
        return None

    async def delete_memory(self, memory_id: str) -> bool:
        """Delete memory by ID."""
        if memory_id in self.store:
            del self.store[memory_id]
            return True
        return False

    async def clear_all(self) -> None:
        """Clear all memories."""
        self.store.clear()

    async def close(self) -> None:
        """Close the store (no-op for in-memory)."""
        pass

    # Compatibility methods for VectorStoreService interface
    async def add(self, texts: list[str], metadatas: list[dict[str, Any]]) -> None:
        """Add multiple texts with metadata."""
        for i, (text, metadata) in enumerate(zip(texts, metadatas, strict=False)):
            await self.add_memory(f"memory_{i}", text, metadata)

    async def query(self, query_texts: list[str], n_results: int = 5) -> dict[str, Any]:
        """Query for similar texts."""
        all_results = []
        for query in query_texts:
            results = await self.search_memories(query, n_results)
            all_results.append(results)

        return {"results": all_results}

    async def upsert(
        self, ids: list[str], documents: list[str], metadatas: list[dict[str, Any]]
    ) -> None:
        """Upsert documents."""
        for doc_id, doc, metadata in zip(ids, documents, metadatas, strict=False):
            await self.add_memory(doc_id, doc, metadata)

    async def get(self, ids: list[str]) -> dict[str, Any]:
        """Get documents by IDs."""
        results = []
        for doc_id in ids:
            memory = await self.get_memory(doc_id)
            if memory:
                results.append(memory)
        return {"documents": results}

    async def delete(self, ids: list[str]) -> None:
        """Delete documents by IDs."""
        for doc_id in ids:
            await self.delete_memory(doc_id)

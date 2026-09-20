from __future__ import annotations

from typing import Any, Callable

from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Tries to use ChromaDB if available; falls back to an in-memory store.
    The embedding_fn parameter allows injection of mock embeddings for tests.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

        try:
            import chromadb  # noqa: F401

            # TODO: initialize chromadb client + collection
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        # TODO: build a normalized stored record for one document
        metadata = dict(doc.metadata) if doc.metadata else {}
        if "doc_id" not in metadata:
            metadata["doc_id"] = doc.id
            
        return {
            "id": str(self._next_index),
            "content": doc.content,
            "metadata": metadata,
            "embedding": self._embedding_fn(doc.content),
        }

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        # TODO: run in-memory similarity search over provided records
        query_emb = self._embedding_fn(query)
        results = []
        for record in records:
            score = _dot(query_emb, record["embedding"])
            res_record = {k:v for k,v in record.items() if k !="embedding"}
            res_record["score"] = score
            results.append(res_record)
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        # TODO: embed each doc and add to store
        for doc in docs:
            record = self._make_record(doc)
            self._store.append(record)
            self._next_index += 1

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        # TODO: embed query, compute similarities, return top_k
        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        # TODO
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        # TODO: filter by metadata, then search among filtered chunks
        filtered = [r for r in self._store if self._matches_metadata(r, metadata_filter)]
        return self._search_records(query, filtered, top_k)

    def _matches_metadata(self, record: dict, metadata_filter: dict) -> bool:
        if not metadata_filter:
            return True
        for key, value in metadata_filter.items():
            if record["metadata"].get(key) != value:
                return False
        return True

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        # TODO: remove all stored chunks where metadata['doc_id'] == doc_id
        initial_len = len(self._store)
        
        # Giữ lại những phần tử có metadata['doc_id'] khác với doc_id truyền vào
        self._store = [
            record for record in self._store 
            if record["metadata"].get("doc_id") != doc_id
        ]
        
        # Nếu độ dài thay đổi nghĩa là đã xóa thành công
        return len(self._store) < initial_len

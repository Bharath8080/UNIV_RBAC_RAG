from pathlib import Path
from typing import List, Dict, Any
from langchain_community.document_loaders import PyPDFLoader
from qdrant_client import models

from src.config import COLLECTION_NAME
from src.retriever import get_qdrant_client, get_vector_store
from src.ingester import get_text_splitter
from src.cache import semantic_cache

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def list_indexed_docs() -> List[Dict[str, Any]]:
    """Lists all distinct PDF documents indexed in Qdrant with chunk counts."""
    client = get_qdrant_client()
    if not client.collection_exists(COLLECTION_NAME):
        return []

    results, _ = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=10000,
        with_payload=True,
    )

    doc_map = {}
    for point in results:
        meta = point.payload.get("metadata", {}) if point.payload else {}
        source_doc = meta.get("source_doc")
        tier = meta.get("tier", "public")
        if source_doc:
            key = (source_doc, tier)
            if key not in doc_map:
                doc_map[key] = {"source_doc": source_doc, "tier": tier, "chunks": 0}
            doc_map[key]["chunks"] += 1

    return list(doc_map.values())


def delete_doc(source_doc: str, tier: str) -> bool:
    """Safely deletes all Qdrant chunks for a specific document without affecting others."""
    client = get_qdrant_client()
    if not client.collection_exists(COLLECTION_NAME):
        return False

    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=models.FilterSelector(
            filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="metadata.source_doc",
                        match=models.MatchValue(value=source_doc),
                    ),
                    models.FieldCondition(
                        key="metadata.tier",
                        match=models.MatchValue(value=tier),
                    ),
                ]
            )
        ),
    )

    # Remove physical file if it exists
    file_path = DATA_DIR / tier / source_doc
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception:
            pass

    # Reset cache so deleted document data is not served
    semantic_cache.reset()
    return True


def ingest_uploaded_pdf(file_bytes: bytes, filename: str, tier: str) -> int:
    """Saves an uploaded PDF to data/<tier>/ and indexes its chunks into Qdrant."""
    tier = tier.lower()

    # 1. Delete any existing chunks and old physical file first
    delete_doc(filename, tier)

    # 2. Write the new uploaded file
    target_dir = DATA_DIR / tier
    target_dir.mkdir(parents=True, exist_ok=True)
    target_file = target_dir / filename

    with open(target_file, "wb") as f:
        f.write(file_bytes)

    # 3. Load and chunk PDF
    loader = PyPDFLoader(str(target_file.resolve()))
    docs = loader.load()
    if not docs:
        return 0

    for doc in docs:
        doc.metadata["tier"] = tier
        doc.metadata["source_doc"] = filename

    splitter = get_text_splitter()
    chunks = splitter.split_documents(docs)
    for chunk in chunks:
        chunk.metadata["tier"] = tier
        chunk.metadata["source_doc"] = filename

    vector_store = get_vector_store()
    vector_store.add_documents(chunks)

    # Reset cache so fresh data takes immediate effect
    semantic_cache.reset()
    return len(chunks)

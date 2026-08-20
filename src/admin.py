from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from qdrant_client import models

from src.config import COLLECTION_NAME
from src.retriever import get_qdrant_client, get_vector_store
from src.ingester import get_text_splitter
from src.cache import semantic_cache

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def list_indexed_docs():
    # Return all distinct indexed PDFs with their role tiers and chunk counts
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


def delete_doc(source_doc, tier):
    # 1. Delete vector points matching document name and tier
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

    # 2. Remove physical PDF file if present
    file_path = DATA_DIR / tier / source_doc
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception:
            pass

    # 3. Clear cache so stale answers aren't returned
    semantic_cache.reset()
    return True


def ingest_uploaded_pdf(file_bytes, filename, tier):
    tier = tier.lower()

    # 1. Delete any existing copy first
    delete_doc(filename, tier)

    # 2. Save uploaded PDF to role tier directory
    target_dir = DATA_DIR / tier
    target_dir.mkdir(parents=True, exist_ok=True)
    target_file = target_dir / filename

    with open(target_file, "wb") as f:
        f.write(file_bytes)

    # 3. Load and split PDF into chunks
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

    # 4. Add chunks to Qdrant vector store and reset cache
    vector_store = get_vector_store()
    vector_store.add_documents(chunks)

    semantic_cache.reset()
    return len(chunks)

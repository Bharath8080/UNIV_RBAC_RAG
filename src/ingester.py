from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.retriever import get_vector_store
from src.config import CHUNK_SIZE, CHUNK_OVERLAP

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

KNOWN_TIERS = ("public", "faculty", "advisor", "dean")


def get_text_splitter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " "],
    )


def determine_tier_from_path(file_path: Path) -> str:
    """Extract tier ('public', 'faculty', 'advisor', 'dean') from parent directory name."""
    for parent in file_path.parents:
        if parent.name.lower() in KNOWN_TIERS:
            return parent.name.lower()
    return "public"


def ingest_directory(data_dir: str | Path = DATA_DIR) -> int:
    """
    Recursively scans the data directory for PDFs, tags each chunk with:
    - metadata['tier']: 'public' | 'faculty' | 'advisor' | 'dean'
    - metadata['source_doc']: filename (e.g. 'campus_policies_2025.pdf')
    and indexes them into the Qdrant vector store.
    """
    path = Path(data_dir)
    if not path.exists():
        print(f"Data directory '{path}' does not exist.")
        return 0

    pdf_files = list(path.rglob("*.pdf"))
    if not pdf_files:
        print(f"No PDF documents found in '{path}'.")
        return 0

    all_chunks = []
    splitter = get_text_splitter()

    for pdf_path in pdf_files:
        tier = determine_tier_from_path(pdf_path)
        loader = PyPDFLoader(str(pdf_path))
        try:
            docs = loader.load()
        except Exception as e:
            print(f"Error loading {pdf_path}: {e}")
            continue

        for doc in docs:
            doc.metadata["tier"] = tier
            doc.metadata["source_doc"] = pdf_path.name

        chunks = splitter.split_documents(docs)
        for chunk in chunks:
            chunk.metadata["tier"] = tier
            chunk.metadata["source_doc"] = pdf_path.name

        all_chunks.extend(chunks)
        print(f"  Processed [{tier}] {pdf_path.name} -> {len(chunks)} chunks")

    if not all_chunks:
        print("No chunks generated.")
        return 0

    vector_store = get_vector_store()
    vector_store.add_documents(all_chunks)
    print(f"\nSuccessfully indexed {len(all_chunks)} chunks across {len(pdf_files)} documents into Qdrant.")
    return len(all_chunks)


def ingest_file(file_path: str | Path, tier: str | None = None) -> int:
    path = Path(file_path)
    if not path.exists():
        return 0

    detected_tier = tier or determine_tier_from_path(path)
    loader = PyPDFLoader(str(path))
    docs = loader.load()
    if not docs:
        return 0

    for doc in docs:
        doc.metadata["tier"] = detected_tier
        doc.metadata["source_doc"] = path.name

    splitter = get_text_splitter()
    chunks = splitter.split_documents(docs)
    for chunk in chunks:
        chunk.metadata["tier"] = detected_tier
        chunk.metadata["source_doc"] = path.name

    vector_store = get_vector_store()
    vector_store.add_documents(chunks)
    return len(chunks)


if __name__ == "__main__":
    ingest_directory()

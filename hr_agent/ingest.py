"""Builds the search index from the documents in the docs directory."""

from pathlib import Path

from dotenv import load_dotenv
from google import genai

from .knowledge import (DATA_DIR, CHUNKS_PATH, INDEX_PATH, build_index, chunk_documents,
                        embed, load_documents, save_index)

DOCS_DIR = DATA_DIR.parent / "docs"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def main() -> None:
    load_dotenv(Path(__file__).resolve().parent / ".env")
    client = genai.Client()

    documents = load_documents(DOCS_DIR)
    if not documents:
        raise SystemExit(f"Keine lesbaren PDFs in {DOCS_DIR} gefunden.")    
    records = []
    for doc in documents:
        for chunk in chunk_documents(doc["text"], CHUNK_SIZE, CHUNK_OVERLAP):
            records.append({
                "chunk_id": len(records),
                "source": doc["source"],
                "page_number": doc["page_number"],
                "text": chunk,
            })

    vectors = embed(client, [r["text"] for r in records], "RETRIEVAL_DOCUMENT")
    index = build_index(vectors)
    save_index(index, records)

    print("--------------------------------")
    print(f"{len(documents)} pages from {len({r['source'] for r in records})} files, "
          f"{len(records)} Chunks -> {INDEX_PATH.name}, {CHUNKS_PATH.name}")


if __name__ == "__main__":
    main()
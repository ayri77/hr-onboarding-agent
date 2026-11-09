""" Knowledge base for the HR agent. """

from pathlib import Path
from pypdf import PdfReader
from google import genai
import numpy as np
import faiss
import json

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
INDEX_PATH = DATA_DIR / "index.faiss"
CHUNKS_PATH = DATA_DIR / "chunks.json"

_index: faiss.Index | None = None
_chunks: list[dict] | None = None
_client: genai.Client | None = None


def load_documents(docs_dir: Path) -> list[dict[str, str | int]]:
    """Loads documents from the given directory."""
    
    documents = []
    for file in docs_dir.glob("*.pdf"):
        reader = PdfReader(file)
        symbols_count = 0
        pages_count = 0
        for page_number, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            if text:
                documents.append({
                    'source': file.name,
                    'page_number': page_number,
                    'text': text
                })
                symbols_count += len(text)
                pages_count += 1
        
        if symbols_count > 0:
            print("--------------------------------")
            print("File: ", file)
            print(f"Found {pages_count} pages in {file}")
            print("Total Symbols: ", symbols_count)
        else:
            print("Warning: No symbols found in file: ", file, ". Probably a scanned file.")
    
    return documents


def chunk_documents(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """Chunks the given text into smaller chunks with the given chunk size and overlap."""

    text_chunks = []
    start = 0
    

    if chunk_size <= 0 or not 0 <= chunk_overlap < chunk_size:
        raise ValueError("Invalid chunk size or overlap")

    while start < len(text):
        end = min(start + chunk_size, len(text))

        if end < len(text):
            new_str = text.rfind('\n', start + chunk_overlap + 1, end)
            if new_str != -1:
                end = new_str

        text_chunks.append(text[start:end])

        if end == len(text):
            break

        # next chunk starts at the beginning of a line, roughly `chunk_overlap` before `end`
        new_start = text.rfind('\n', 0, end - chunk_overlap) + 1
        start = new_start if new_start > start else end - chunk_overlap

    return text_chunks


def embed(client, text, task_type) -> np.ndarray:
    """Embeds the given text into a vector."""

    response = client.models.embed_content(
            model="gemini-embedding-001", 
            contents=text,
            config=genai.types.EmbedContentConfig(task_type=task_type, output_dimensionality=768),
        )
    vectors = np.asarray(
            [emb.values for emb in response.embeddings],
            dtype=np.float32,
        )
    
    faiss.normalize_L2(vectors)
    return vectors


def build_index(vectors: np.ndarray) -> faiss.Index:
    """Builds the index from the given vectors."""

    if vectors.ndim != 2:
        raise ValueError("Expected 2D array of embeddings")

    if vectors.shape[0] == 0:
        raise ValueError("No embeddings provided")

    dimension = vectors.shape[1]
    index = faiss.IndexFlatIP(dimension)    
    
    index.add(vectors)

    return index


def save_index(index: faiss.Index, records: list[dict]) -> None:
    """Saves the index and records to the given paths."""

    DATA_DIR.mkdir(exist_ok=True)
    faiss.write_index(index, str(INDEX_PATH))
    CHUNKS_PATH.write_text(json.dumps(records, ensure_ascii=False, indent=1), encoding="utf-8")


def _load() -> tuple[faiss.Index, list[dict], genai.Client]:
    """Loads the index and records from the given paths."""
    
    global _index, _chunks, _client
    if _index is None:
        if not INDEX_PATH.exists():
            raise FileNotFoundError("Kein Index. Zuerst `python -m hr_agent.ingest` ausführen.")
        _index = faiss.read_index(str(INDEX_PATH))
        _chunks = json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))
        _client = genai.Client()
    return _index, _chunks, _client


def search(query: str, k: int = 4, min_score: float = 0.5) -> list[dict]:
    """Returns the top-k chunks for the query with source, page, text and score."""

    index, chunks, client = _load()
    q = embed(client, [query], "RETRIEVAL_QUERY")
    scores, ids = index.search(q, k)
    hits = []
    for score, i in zip(scores[0], ids[0]):
        if i == -1 or score < min_score:
            continue
        rec = chunks[int(i)]
        hits.append({"source": rec["source"], "page": rec["page_number"],
                     "text": rec["text"], "score": round(float(score), 3)})
    return hits


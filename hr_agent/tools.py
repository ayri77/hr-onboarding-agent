"""Tools the agent can call."""

from .knowledge import search


def search_docs(query: str) -> dict:
    """Search the onboarding documents for passages relevant to the question.

    Returns up to four hits with source file, page, text and similarity score.
    Call this before answering any question about the company.
    """
    hits = search(query, k=4, min_score=0.5)
    if not hits:
        return {"status": "empty", "message": "Keine passenden Textstellen gefunden.", "results": []}
    return {"status": "ok", "results": hits}

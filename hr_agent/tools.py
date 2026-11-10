"""Tools the agent can call."""

from .knowledge import DATA_DIR, search

import json
from datetime import datetime, timezone

TOPICS = ["erster_tag", "arbeitszeit", "it_zugang", "geraete", "urlaub", "krankmeldung", "sonstiges"]
TOPICS_PATH = DATA_DIR / "topics.jsonl"


def search_docs(query: str) -> dict:
    """Search the onboarding documents for passages relevant to the question.

    Returns up to four hits with source file, page, text and similarity score.
    Call this before answering any question about the company.
    """
    hits = search(query, k=4, min_score=0.5)
    if not hits:
        return {"status": "empty", "message": "Keine passenden Textstellen gefunden.", "results": []}
    return {"status": "ok", "results": hits}


def log_topic(topic: str, found_in_docs: bool) -> dict:
    """Log the topic of an answered question for HR statistics.

    topic: one of the TOPICS list, anything else becomes "sonstiges".
    found_in_docs: whether the documents contained the answer.
    Stores only topic, flag and timestamp. No question text, no person.
    """

    if topic not in TOPICS:
        topic = "sonstiges"    

    DATA_DIR.mkdir(exist_ok=True)
    with open(TOPICS_PATH, "a", encoding="utf-8") as f:
        f.write(
            json.dumps(
                {
                    "topic": topic, 
                    "found_in_docs": found_in_docs, 
                    "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds")
                }
            ) + "\n"
        )
    return {"status": "ok", "topic": topic}
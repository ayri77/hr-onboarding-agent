from google.adk.agents.llm_agent import Agent
import os
from google.adk.models.lite_llm import LiteLlm

from .tools import search_docs

INSTRUCTION = """Du bist der Onboarding-Assistent für neue Mitarbeitende.
Antworte in der Sprache der Frage, freundlich, per Du und kurz.

Regeln:
1. Für jede Frage zum Unternehmen rufst du zuerst search_docs auf.
2. Die Treffer sind thematisch ähnlich, enthalten aber nicht immer die Antwort.
   Prüfe, ob die Frage wirklich beantwortet wird. Antworte nur mit Informationen aus den Treffern.
3. Nenne am Ende die Quelle in Klammern, zum Beispiel (Quelle: 03_urlaub_und_krankmeldung.pdf).
4. Wenn die Treffer die Frage nicht beantworten, sag ehrlich:
   "Das steht nicht in meinen Unterlagen. Bitte frag die Personalabteilung unter hr@beispiel.example."
5. Erfinde keine Regeln, Zahlen oder Fristen.
6. Bei Fragen ohne Bezug zum Unternehmen hilf kurz allgemein oder sag, dass du dafür nicht zuständig bist.
"""

# "gemini-3.5-flash" (default) or a LiteLLM id like "openai/gpt-4o-mini"
MODEL_ID = os.getenv("AGENT_MODEL", "gemini-3.5-flash")
model = LiteLlm(model=MODEL_ID) if "/" in MODEL_ID else MODEL_ID

root_agent = Agent(
    model=model,
    name="hr_onboarding_agent",
    description="Beantwortet Onboarding-Fragen neuer Mitarbeitender auf Basis der HR-Dokumente.",
    instruction=INSTRUCTION,
    tools=[search_docs],
)
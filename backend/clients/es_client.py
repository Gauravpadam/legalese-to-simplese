"""
es_client.py

Connect to Elasticsearch, create an index, chunk input text, call your LLM service
to classify clause tags, and index the chunks with tags.

Notes:
- We REMOVE risk_score entirely (store only tags + optional section/explanation).
- We CALL your existing LLM function `ask_question(system, human)` (imported).
- You pass in full text (from your own OCR step) to `tag_and_index_text(...)`.
"""

import os
import json
from typing import List, Tuple, Dict, Optional
from elasticsearch import Elasticsearch, helpers

# -------------------------------------------------------------------
# IMPORT YOUR LLM CALL
# -------------------------------------------------------------------
# Make sure you have this in your project:
# from llm_service import ask_question
#
# `ask_question(system_message: str, human_message: str) -> str` (async)
# that returns STRICT JSON as string: {"risk_tags":[...], "explanation":"...", "section_guess":"..."}
try:
    from llm_service import ask_question  # noqa: F401
except Exception:
    # If you want to run this file alone, replace with your implementation.
    raise ImportError("Please provide `ask_question(system, human)` in llm_service.py")


# -------------------------------------------------------------------
# CONTROLLED TAG VOCAB
# -------------------------------------------------------------------
TAG_VOCAB: List[Tuple[str, str]] = [
    # Liability / Indemnity
    ("liability_unlimited", "Unlimited liability or no cap"),
    ("indemnity_broad", "Indemnify/defend/hold harmless (one-sided or broad)"),
    ("exclude_conseq_damages", "Excludes consequential/indirect damages"),
    # Termination
    ("termination_convenience", "Termination for convenience / without cause"),
    ("termination_immediate", "Immediate termination rights"),
    ("termination_without_cause", "Termination without cause"),
    # Renewal / Duration
    ("auto_renewal", "Auto-renewal or evergreen term"),
    ("perpetual_term", "Perpetual term"),
    ("minimum_term", "Minimum locked-in term"),
    # Payment / Penalties
    ("holdover_double_rent", "Holdover damages 2x monthly rent"),
    ("late_payment_penalty", "Late fees/penalties"),
    ("interest_free_deposit", "Interest-free security deposit"),
    # Confidentiality / Data
    ("confidentiality_perpetual", "Perpetual confidentiality"),
    ("data_sharing_third_parties", "Broad third-party data sharing"),
    ("breach_notice_hours", "Breach notice within X hours (24/48/72)"),
    # IP / Ownership
    ("ip_assignment", "Assignment of IP / all rights"),
    ("royalty_free_license", "Royalty-free perpetual license"),
    # Disputes / Governing Law
    ("mandatory_arbitration", "Binding/mandatory arbitration"),
    ("exclusive_jurisdiction", "Exclusive jurisdiction"),
    ("governing_law_clause", "Governing law clause"),
    # Usage restrictions (rental)
    ("no_subletting", "No subletting"),
    ("use_restriction_residential", "Residential use only"),
    # Misc
    ("notwithstanding_clause", "Contains 'notwithstanding'"),
    ("best_efforts_clause", "Contains 'best_efforts'"),
    ("sole_discretion", "At its sole discretion"),
]
ALLOWED_TAGS = [slug for slug, _ in TAG_VOCAB]


# -------------------------------------------------------------------
# LLM PROMPTS (only tags; no risk_score)
# -------------------------------------------------------------------
LLM_SYSTEM_PROMPT = f"""
You are a contracts clause tagger.

Return STRICT JSON with keys:
- "risk_tags": array of tag slugs chosen ONLY from this allowed list:
{json.dumps(ALLOWED_TAGS)}
- "explanation": <=30 words plain text describing why these tags were chosen
- "section_guess": one or two words indicating clause type (e.g., "Liability","Termination","Payment","Data","IP","Jurisdiction","Usage","Misc")

Rules:
- Output JSON ONLY (no extra text or markdown).
- If unsure, return "risk_tags": [] and a short neutral explanation.
"""

def build_human_prompt(clause_text: str) -> str:
    return f"""Clause:
-----
{clause_text}
-----

Return JSON ONLY with keys: risk_tags, explanation, section_guess."""

def safe_json_parse(s: str) -> Dict:
    """Parse LLM response and enforce allowed tag set; never raise."""
    try:
        data = json.loads(s)
        if not isinstance(data, dict):
            raise ValueError("Expected JSON object")
        data.setdefault("risk_tags", [])
        data.setdefault("explanation", "")
        data.setdefault("section_guess", "Misc")

        # Clean fields
        if not isinstance(data["risk_tags"], list):
            data["risk_tags"] = []
        data["risk_tags"] = [t for t in data["risk_tags"] if t in ALLOWED_TAGS]
        if not isinstance(data["explanation"], str):
            data["explanation"] = ""
        if not isinstance(data["section_guess"], str):
            data["section_guess"] = "Misc"
        return data
    except Exception:
        return {"risk_tags": [], "explanation": "", "section_guess": "Misc"}


# -------------------------------------------------------------------
# CHUNKING
# -------------------------------------------------------------------
def simple_paragraph_chunker(text: str, max_chars: int = 1200, overlap: int = 120) -> List[str]:
    """
    Simple paragraph-aware chunker; you pass FULL TEXT from your OCR.
    """
    paragraphs = [p.strip() for p in (text or "").split("\n") if p.strip()]
    chunks, buf = [], ""
    for p in paragraphs:
        if len(buf) + len(p) + 1 <= max_chars:
            buf = (buf + "\n" + p).strip()
        else:
            if buf:
                chunks.append(buf)
            buf = (buf[-overlap:] + "\n" + p).strip()
    if buf:
        chunks.append(buf)
    return chunks


# -------------------------------------------------------------------
# ELASTICSEARCH HELPERS
# -------------------------------------------------------------------
def es_client(host: Optional[str] = None) -> Elasticsearch:
    """
    Create Elasticsearch client. Set ES_HOST env var or pass host explicitly.
    """
    client = Elasticsearch(
    cloud_id='https://my-elasticsearch-project-b07525.es.us-central1.gcp.elastic.cloud:443',
    basic_auth=("elastic", 'SVQ3Y1Y1a0JscUh2YzI0Rmlkd2Q6eTBMVHBudW14Wm53WjFydGM1SFVsZw==')
)
    return Elasticsearch(host or os.getenv("ES_HOST", "http://localhost:9200"), verify_certs=False)

def ensure_index(es: Elasticsearch, index: str):
    """
    Create index with mapping (NO risk_score) if not exists.
    """
    if es.indices.exists(index=index):
        return
    body = {
        "settings": {"index": {"number_of_shards": 1, "number_of_replicas": 0}},
        "mappings": {
            "properties": {
                "doc_id":      {"type": "keyword"},
                "chunk_id":    {"type": "integer"},
                "text":        {"type": "text"},      # BM25
                "section":     {"type": "keyword"},   # from LLM section_guess
                "risk_tags":   {"type": "keyword"},   # ONLY tags (no scores)
                "explanation": {"type": "text"}       # optional human-friendly reason
            }
        }
    }
    es.indices.create(index=index, body=body)


# -------------------------------------------------------------------
# MAIN ENTRYPOINT: TAG + INDEX
# -------------------------------------------------------------------
async def tag_and_index_text(
    full_text: str,
    doc_id: str,
    index_name: str,
    es_host: Optional[str] = None,
    max_chars: int = 1200,
    overlap: int = 120
) -> int:
    """
    - You pass OCR text in `full_text`.
    - We chunk it, ask the LLM for tags (NO risk_score), and index into Elasticsearch.

    Returns: number of chunks indexed.
    """
    es = es_client(es_host)
    ensure_index(es, index_name)

    chunks = simple_paragraph_chunker(full_text, max_chars=max_chars, overlap=overlap)

    actions = []
    for i, ch in enumerate(chunks, start=1):
        raw = await ask_question(LLM_SYSTEM_PROMPT, build_human_prompt(ch))
        llm = safe_json_parse(raw or "")
        actions.append({
            "_index": index_name,
            "_source": {
                "doc_id": doc_id,
                "chunk_id": i,
                "text": ch,
                "section": llm.get("section_guess", "Misc"),
                "risk_tags": llm.get("risk_tags", []),
                "explanation": llm.get("explanation", "")
            }
        })

    if actions:
        helpers.bulk(es, actions)
        es.indices.refresh(index=index_name)
    return len(actions)

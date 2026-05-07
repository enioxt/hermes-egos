"""
7 técnicas anti-alucinação para respostas RAG.
Port de docs/knowledge/ANTI_HALLUCINATION_COMPLETE_GUIDE.md (EGOS kernel).

Pitch: "Toda resposta tem prova. Você clica e vê o documento original.
        Se não tem prova, o sistema diz 'não encontro'."

Inclui: Intent Guardrails (detecção de prompt injection ANTES de consultar KB).
Vault integration [GROK-EVD-006]: verifica evidence_verified_knowledge via Supabase REST
  antes de aceitar resposta sem chunks RAG. Opt-in: SUPABASE_URL + SUPABASE_ANON_KEY + VAULT_TENANT_ID.
"""

import re
import os
import json
import urllib.request
from typing import Optional


# ─── Evidence Vault REST integration [GROK-EVD-006] ──────────────────────────

_SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
_SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
_VAULT_TENANT_ID = os.environ.get("VAULT_TENANT_ID", "")
_VAULT_ENABLED = bool(_SUPABASE_URL and _SUPABASE_ANON_KEY and _VAULT_TENANT_ID)


def check_vault_evidence(query: str, tenant_id: str | None = None) -> dict:
    """
    Verifica se há VerifiedKnowledge no vault que cubra a query.
    Chamado quando validate_rag_response não encontra chunks RAG suficientes.

    Returns:
        {
          'found': bool,
          'verified': bool,
          'evidence_ids': list[str],
          'statements': list[str],
          'source': 'vault' | 'none'
        }
    """
    t_id = tenant_id or _VAULT_TENANT_ID
    if not _VAULT_ENABLED or not t_id:
        return {"found": False, "verified": False, "evidence_ids": [], "statements": [], "source": "none"}

    # Truncar query para busca
    search_term = query[:100].replace("'", "''")

    try:
        params = f"tenant_id=eq.{t_id}&approved_for_output=eq.true&statement=ilike.%25{urllib.parse.quote(search_term[:80])}%25&select=id,statement&limit=3"
        url = f"{_SUPABASE_URL}/rest/v1/evidence_verified_knowledge?{params}"
        req = urllib.request.Request(
            url,
            headers={
                "apikey": _SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {_SUPABASE_ANON_KEY}",
            },
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode())
            if data:
                return {
                    "found": True,
                    "verified": True,
                    "evidence_ids": [r["id"] for r in data],
                    "statements": [r["statement"] for r in data],
                    "source": "vault",
                }
    except Exception:
        pass  # Non-blocking — vault check failure does not block response

    return {"found": False, "verified": False, "evidence_ids": [], "statements": [], "source": "none"}


# ─── urllib.parse shim (Python 3.9+ stdlib) ───────────────────────────────────
try:
    from urllib.parse import quote as _urllib_parse_quote
    # Patch the module-level urllib.parse reference used in check_vault_evidence
    import urllib.parse
except ImportError:
    pass


# ─── Intent Guardrails (Pré-geração: detectar prompt injection) ────────────────

_INJECTION_PATTERNS = [
    # Tentativas clássicas de jailbreak
    r"ignor[ae]\s+(todas?\s+as?\s+)?(instru[cç][oõ]es|regras|prompt|guidelines)",
    r"esqueç[ae]\s+(tudo|as?\s+instru[cç][oõ]es)",
    r"você\s+é\s+(agora|um)\s+(outro|diferente|novo)\s+(assistente|bot|ai)",
    r"finja\s+que\s+você\s+é",
    r"act\s+as\s+if\s+you\s+are",
    r"ignore\s+(all\s+)?(previous\s+)?instructions",
    r"reveal\s+(your\s+)?(system\s+)?prompt",
    r"mostre?\s+(o\s+)?(seu\s+)?(prompt|instrução|system)\s+(do\s+sistema)?",
    r"que\s+instruç[oõ]es\s+(você|voce)\s+recebeu",
    # Tentativas de extração de dados
    r"(liste|me\s+diga|mostre)\s+(todos?\s+os?\s+)?(document|arquivo|senha|password|chave|key|token)",
    r"qual\s+(é|e)\s+(a\s+)?(senha|password|token|chave\s+de\s+api)",
    r"quais?\s+(são|sao)\s+(os?\s+)?(dados|credenciais|config)",
]

import re

_INJECTION_RE = [re.compile(p, re.IGNORECASE) for p in _INJECTION_PATTERNS]


def detect_prompt_injection(text: str) -> dict:
    """
    Detecta tentativas de prompt injection ANTES de processar a query.
    Chamado como Intent Guardrail (pré-geração).

    Returns: {'is_injection': bool, 'confidence': float, 'matched_pattern': str | None}
    """
    for pattern in _INJECTION_RE:
        m = pattern.search(text)
        if m:
            return {
                "is_injection": True,
                "confidence": 0.95,
                "matched_pattern": pattern.pattern,
                "matched_text": m.group()[:100],
                "safe_response": (
                    "Não consigo processar essa solicitação. "
                    "Posso ajudar com consultas sobre os documentos da base de conhecimento."
                ),
            }

    # Score heurístico simples para tentativas mais sutis
    suspicious_score = 0.0
    if "system" in text.lower() and "prompt" in text.lower():
        suspicious_score += 0.4
    if any(w in text.lower() for w in ["jailbreak", "dan", "do anything now"]):
        suspicious_score += 0.8
    if len(text) > 500 and text.count("\n") > 10:
        suspicious_score += 0.2  # Texto muito longo com muitas linhas = suspeito

    return {
        "is_injection": suspicious_score >= 0.7,
        "confidence": suspicious_score,
        "matched_pattern": None,
        "matched_text": None,
    }


# ─── Técnica 1: Provenance (cadeia de custódia) ────────────────────────────────

def build_provenance_response(
    answer: str,
    chunks: list[dict],
    query: str,
) -> dict:
    """
    Constrói resposta RAG com cadeia de custódia completa.
    chunks: lista de {'document_id', 'title', 'text', 'score', 'source'}
    """
    citations = []
    for i, chunk in enumerate(chunks, 1):
        citations.append({
            "ref": f"[{i}]",
            "document_id": chunk.get("document_id", ""),
            "title": chunk.get("title", "Documento"),
            "text_excerpt": chunk.get("text", "")[:200],
            "score": round(chunk.get("score", 0.0), 3),
            "source": chunk.get("source", "knowledge_base"),
        })

    citation_text = "\n".join(
        f"{c['ref']} {c['title']}: \"{c['text_excerpt']}...\""
        for c in citations
    )

    return {
        "answer": answer,
        "has_provenance": len(citations) > 0,
        "citations": citations,
        "citation_count": len(citations),
        "formatted_response": f"{answer}\n\n**Fontes:**\n{citation_text}" if citations else answer,
        "confidence": "grounded" if citations else "ungrounded",
    }


# ─── Técnica 3: RAG Context Compression ────────────────────────────────────────

def compress_rag_context(chunks: list[dict], max_chunks: int = 5, max_tokens_per_chunk: int = 300) -> list[dict]:
    """
    Seleciona e comprime os chunks mais relevantes.
    Evita passar contexto demais para o LLM (reduz alucinação por confusão).
    """
    # Ordenar por score decrescente
    sorted_chunks = sorted(chunks, key=lambda c: c.get("score", 0), reverse=True)

    # Pegar top-N
    top = sorted_chunks[:max_chunks]

    # Truncar texto se muito longo
    for chunk in top:
        text = chunk.get("text", "")
        # Estimar tokens (aprox 4 chars/token)
        max_chars = max_tokens_per_chunk * 4
        if len(text) > max_chars:
            chunk["text"] = text[:max_chars] + "..."
            chunk["truncated"] = True

    return top


# ─── Técnica 4: ATRiAN — validação ética pós-geração ──────────────────────────

_ABSOLUTE_CLAIM_RE = re.compile(
    r'\b(É certo que|Definitivamente|100%|absolutamente|garantido|sem dúvida|com certeza)\b',
    re.IGNORECASE,
)
_FALSE_PROMISE_RE = re.compile(
    r'\b(Vou fazer|Resolvo|Garantimos|Certamente vou|Farei isso)\b',
    re.IGNORECASE,
)
_NUMBER_WITHOUT_SOURCE_RE = re.compile(r'R\$\s*[\d.,]+|[\d.]+%|\d+\s+anos?')


def atrian_validate(response_text: str, context_chunks: list[dict] = None) -> dict:
    """
    Técnica 4: Filtro pós-geração (port de packages/shared/src/atrian.ts).
    Detecta claims absolutos, promessas falsas e números sem fonte.
    """
    violations = []

    # Check 1: Claims absolutos
    for m in _ABSOLUTE_CLAIM_RE.finditer(response_text):
        violations.append({
            "type": "absolute_claim",
            "severity": "warning",
            "text": m.group(),
            "position": m.start(),
        })

    # Check 2: Promessas falsas
    for m in _FALSE_PROMISE_RE.finditer(response_text):
        violations.append({
            "type": "false_promise",
            "severity": "critical",
            "text": m.group(),
            "position": m.start(),
        })

    # Check 3: Números sem fonte citada
    chunks_text = " ".join(c.get("text", "") for c in (context_chunks or []))
    for m in _NUMBER_WITHOUT_SOURCE_RE.finditer(response_text):
        val = m.group()
        # Verificar se o número está nos chunks de contexto
        if val not in chunks_text and len(violations) < 10:
            violations.append({
                "type": "unsourced_number",
                "severity": "error",
                "text": val,
                "position": m.start(),
            })

    score = max(0, 100 - sum(
        {"warning": 5, "error": 15, "critical": 30}.get(v["severity"], 0)
        for v in violations
    ))

    passed = not any(v["severity"] in ("critical", "error") for v in violations)

    return {
        "passed": passed,
        "score": score,
        "violations": violations,
        "violation_count": len(violations),
        "action": "block" if not passed else "pass",
    }


# ─── Técnica 6: Confidence Scoring ─────────────────────────────────────────────

def compute_confidence(chunks: list[dict], threshold: float = 0.7) -> dict:
    """
    Técnica 6: Calcula confiança da resposta baseada nos scores dos chunks.
    Se confiança baixa → instrui a dizer "não encontro".
    """
    if not chunks:
        return {
            "confidence": 0.0,
            "level": "none",
            "should_answer": False,
            "message": "Não encontrei informação relevante na base de conhecimento.",
        }

    avg_score = sum(c.get("score", 0) for c in chunks) / len(chunks)
    top_score = max(c.get("score", 0) for c in chunks)

    level = "high" if top_score >= 0.85 else "medium" if top_score >= threshold else "low"
    should_answer = top_score >= threshold

    return {
        "confidence": round(top_score, 3),
        "avg_confidence": round(avg_score, 3),
        "level": level,
        "should_answer": should_answer,
        "message": None if should_answer else (
            "Não encontrei informação suficientemente confiável na base de conhecimento. "
            "Por favor, consulte diretamente a documentação ou um profissional."
        ),
    }


# ─── Tool principal: validate_rag_response ──────────────────────────────────────

def validate_rag_response(
    response_text: str,
    chunks: list[dict] = None,
    query: str = "",
) -> dict:
    """
    Tool unificada: aplica todas as 4 técnicas implementáveis sem RAG externo.
    Retorna resposta final com provenance + validação ATRiAN + confidence.

    chunks formato: [{'document_id', 'title', 'text', 'score', 'source'}]
    """
    chunks = chunks or []

    # Técnica 3: Comprimir contexto
    compressed = compress_rag_context(chunks)

    # Técnica 6: Confidence scoring
    conf = compute_confidence(compressed)

    if not conf["should_answer"]:
        # Técnica 8 [GROK-EVD-006]: fallback to Evidence Vault before refusing
        vault = check_vault_evidence(query)
        if vault["found"] and vault["verified"]:
            vault_response = (
                " ".join(vault["statements"][:2])
                + " [Fonte: Evidence Vault verificado]"
            )
            return {
                "ok": True,
                "action": "respond_from_vault",
                "final_response": vault_response,
                "confidence": conf,
                "provenance": [{"source": "vault", "id": eid} for eid in vault["evidence_ids"]],
                "vault": vault,
                "atrian_passed": True,
            }
        return {
            "ok": True,
            "action": "refuse_low_confidence",
            "final_response": conf["message"],
            "confidence": conf,
            "provenance": [],
            "vault_checked": _VAULT_ENABLED,
            "vault_found": False,
            "atrian_passed": True,
        }

    # Técnica 4: ATRiAN validation
    atrian = atrian_validate(response_text, compressed)

    if not atrian["passed"]:
        # Resposta bloqueada — retornar mensagem segura
        return {
            "ok": True,
            "action": "block_atrian_violation",
            "final_response": (
                "Não consigo confirmar esta informação com os documentos disponíveis. "
                "Por favor, consulte a fonte original ou um profissional."
            ),
            "atrian": atrian,
            "confidence": conf,
            "provenance": [],
        }

    # Técnica 1: Provenance
    provenance = build_provenance_response(response_text, compressed, query)

    return {
        "ok": True,
        "action": "respond_with_provenance",
        "final_response": provenance["formatted_response"],
        "confidence": conf,
        "atrian": atrian,
        "provenance": provenance["citations"],
        "citation_count": provenance["citation_count"],
    }

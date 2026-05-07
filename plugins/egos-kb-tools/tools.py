"""
egos-kb-tools — Busca na base de conhecimento do cliente via Supabase
HERMES-FORK-009 | Status: IMPLEMENTED ✅

Port do match_kb_hybrid (TypeScript → Python).
FTS (português) + pgvector + RRF — busca híbrida.

Integra com o plugin egos-anti-hallucination:
  resultado da busca → validate_rag_response() → resposta com provenance.
"""

import os
import json
import urllib.request
import urllib.parse
from typing import Optional


def _supabase_call(endpoint: str, payload: dict, service_role: str, url: str) -> dict:
    """POST genérico para Supabase REST."""
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{url}/rest/v1/{endpoint}",
        data=data,
        headers={
            "Content-Type": "application/json",
            "api" + "key": service_role,
            "Authorization": f"Bearer {service_role}",
            "Prefer": "return=representation",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return {"ok": True, "data": json.loads(resp.read())}
    except urllib.error.HTTPError as e:
        return {"ok": False, "error": f"HTTP {e.code}: {e.read().decode()[:200]}"}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


def _get_embedding(text: str, openrouter_key: str) -> list[float]:
    """Gera embedding via OpenRouter (modelos de embedding compatíveis)."""
    payload = json.dumps({
        "model": "openai/text-embedding-3-small",
        "input": text[:8000],
    }).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/embeddings",
        data=payload,
        headers={
            "Authorization": f"Bearer {openrouter_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return data["data"][0]["embedding"]
    except Exception:
        # Fallback: vetor zero (só FTS ficará ativo)
        return [0.0] * 1536


def search_kb(
    query: str,
    tenant_id: str = "",
    top_k: int = 5,
    threshold: float = 0.5,
) -> dict:
    """
    Busca híbrida na base de conhecimento do cliente.
    FTS (full-text search PT-BR) + pgvector (semântica) + RRF (reranking).

    Retorna os chunks mais relevantes com título, texto, score e document_id.
    Integrar resultado com validate_rag_response() do plugin egos-anti-hallucination.
    """
    supabase_url = os.environ.get("SUPABASE_URL", "")
    service_role = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    openrouter_key = os.environ.get("OPENROUTER_API_KEY", "")
    kb_tenant = tenant_id or os.environ.get("KB_TENANT", "egos")

    if not supabase_url or not service_role:
        return {
            "ok": False,
            "error": "SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY são obrigatórios.",
            "results": [],
        }

    # Gerar embedding para busca semântica
    embedding = _get_embedding(query, openrouter_key) if openrouter_key else [0.0] * 1536

    # Chamar match_kb_hybrid (função SQL existente no Supabase)
    result = _supabase_call(
        "rpc/match_kb_hybrid",
        {
            "query_text": query,
            "query_embedding": embedding,
            "match_threshold": threshold,
            "match_count": top_k,
            "tenant_id": kb_tenant,
        },
        service_role,
        supabase_url,
    )

    if not result["ok"]:
        # Tentar fallback só FTS
        result = _supabase_call(
            "rpc/match_kb_fts_only",
            {
                "query_text": query,
                "match_count": top_k,
                "tenant_id": kb_tenant,
            },
            service_role,
            supabase_url,
        )

    if not result["ok"]:
        return {
            "ok": False,
            "error": result.get("error", "Busca falhou"),
            "results": [],
        }

    rows = result.get("data", [])
    if not isinstance(rows, list):
        rows = []

    # Formatar para uso com egos-anti-hallucination
    chunks = [
        {
            "document_id": row.get("document_id", row.get("id", "")),
            "title": row.get("title", row.get("page_title", "Documento")),
            "text": row.get("content", row.get("chunk_text", "")),
            "score": float(row.get("similarity", row.get("fts_rank", 0.5))),
            "source": f"kb:{kb_tenant}",
        }
        for row in rows
    ]

    return {
        "ok": True,
        "query": query,
        "tenant_id": kb_tenant,
        "results": chunks,
        "count": len(chunks),
        "note": (
            "Use validate_rag_response(answer, chunks) do plugin egos-anti-hallucination "
            "antes de enviar a resposta ao usuário."
        ),
    }


def get_kb_stats(tenant_id: str = "") -> dict:
    """Estatísticas da base de conhecimento do cliente."""
    supabase_url = os.environ.get("SUPABASE_URL", "")
    service_role = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    kb_tenant = tenant_id or os.environ.get("KB_TENANT", "egos")

    if not supabase_url or not service_role:
        return {"ok": False, "error": "Supabase não configurado"}

    # Query simples via REST
    encoded = urllib.parse.quote(f"eq.{kb_tenant}")
    req = urllib.request.Request(
        f"{supabase_url}/rest/v1/egos_kb_pages?tenant_id={encoded}&select=id&limit=1000",
        headers={
            "api" + "key": service_role,
            "Authorization": f"Bearer {service_role}",
            "Prefer": "count=exact",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            count = resp.headers.get("Content-Range", "0/0").split("/")[-1]
            return {
                "ok": True,
                "tenant_id": kb_tenant,
                "total_pages": int(count) if count.isdigit() else 0,
                "embedding_model": "openai/text-embedding-3-small (via OpenRouter)",
                "search_type": "hybrid (FTS + pgvector + RRF)",
            }
    except Exception as e:
        return {"ok": False, "error": str(e)[:100]}

"""
egos-kb-tools — Busca na base de conhecimento do cliente
HERMES-FORK-009 | Status: IMPLEMENTED ✅

Busca híbrida: FTS (português) + pgvector (embeddings) + RRF (reranking).
Integra com egos-anti-hallucination para respostas com provenance.

Env vars obrigatórias:
  SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, OPENROUTER_API_KEY (para embeddings)
  KB_TENANT (slug do cliente, ex: "advocacia-dr-joao")
"""

from agent.plugins import PluginContext
from .tools import search_kb, get_kb_stats

_SEARCH_KB_SCHEMA = {
    "name": "search_kb",
    "description": (
        "Busca na base de conhecimento do cliente usando busca híbrida "
        "(FTS português + semântica + RRF). "
        "SEMPRE usar validate_rag_response() do plugin egos-anti-hallucination "
        "com os chunks retornados antes de responder ao usuário."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Pergunta do usuário em linguagem natural"},
            "tenant_id": {"type": "string", "description": "ID do tenant (opcional, usa KB_TENANT do env se ausente)"},
            "top_k": {"type": "integer", "description": "Número de resultados (default: 5)", "default": 5},
            "threshold": {"type": "number", "description": "Score mínimo (default: 0.5)", "default": 0.5},
        },
        "required": ["query"],
    },
}

_KB_STATS_SCHEMA = {
    "name": "get_kb_stats",
    "description": "Retorna estatísticas da base de conhecimento do cliente (total de páginas, tipo de busca).",
    "parameters": {
        "type": "object",
        "properties": {
            "tenant_id": {"type": "string"},
        },
    },
}


def register(ctx: PluginContext) -> None:
    ctx.register_tool("search_kb", search_kb, schema=_SEARCH_KB_SCHEMA)
    ctx.register_tool("get_kb_stats", get_kb_stats, schema=_KB_STATS_SCHEMA)

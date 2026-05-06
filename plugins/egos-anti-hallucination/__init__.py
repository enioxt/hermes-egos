"""
egos-anti-hallucination — 7 técnicas anti-alucinação para respostas RAG
HERMES-FORK-006 | Status: IMPLEMENTED ✅ (4 técnicas ativas, 3 via RAG externo)

Técnicas implementadas neste plugin:
  1. Provenance — cadeia de custódia com fonte de cada informação
  3. RAG Context Compression — seleciona top-5 chunks mais relevantes
  4. ATRiAN — filtro pós-geração (claims absolutos, promessas falsas, números sem fonte)
  6. Confidence Scoring — recusa se confiança < 70%

Técnicas que dependem de integração externa (RAG/eval runner):
  2. Behavioral Eval + Golden Cases — via packages/eval-runner/ (egos kernel)
  5. Hybrid Search (FTS + pgvector + RRF) — via match_kb_hybrid (egos-kb-tools plugin)
  7. Source Ranking — integrado ao Confidence Scoring

Diferencial comercial:
  "Toda resposta tem prova. Você clica e vê o documento original.
   Se não tem prova, o sistema diz 'não encontro'."
"""

from agent.plugins import PluginContext
from .schemas import VALIDATE_RAG_SCHEMA
from .tools import validate_rag_response


def register(ctx: PluginContext) -> None:
    ctx.register_tool("validate_rag_response", validate_rag_response, schema=VALIDATE_RAG_SCHEMA)

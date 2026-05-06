"""
egos-anti-hallucination — 7 técnicas anti-alucinação
HERMES-FORK-006 | Status: in_development

Implementa as 7 técnicas documentadas em:
egos/docs/knowledge/ANTI_HALLUCINATION_COMPLETE_GUIDE.md

1. Provenance — toda resposta RAG retorna cadeia de custódia
2. Behavioral Eval + Golden Cases — testa se IA fala verdade
3. RAG Context Compression — top-5 chunks rerankeados
4. ATRiAN Ethical Validation — filtro pós-geração
5. Hybrid Search (FTS + pgvector + RRF)
6. Confidence Scoring
7. Source Ranking

Diferencial Central EGOS:
"Toda resposta tem prova. Você clica e vê o documento original.
Se não tem prova, o sistema diz 'não encontro'."
"""

from agent.plugins import PluginContext


def register(ctx: PluginContext) -> None:
    # TODO: implementar em HERMES-FORK-006
    raise NotImplementedError("egos-anti-hallucination: NOT IMPLEMENTED — see HERMES-FORK-006 in egos/TASKS.md")

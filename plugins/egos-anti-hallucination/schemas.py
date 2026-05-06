"""Schemas das tools egos-anti-hallucination."""

VALIDATE_RAG_SCHEMA = {
    "name": "validate_rag_response",
    "description": (
        "Valida uma resposta RAG aplicando 4 técnicas anti-alucinação: "
        "(1) Provenance — adiciona cadeia de custódia com fonte de cada informação; "
        "(3) RAG Context Compression — usa só os chunks mais relevantes; "
        "(4) ATRiAN — bloqueia claims absolutos e promessas falsas; "
        "(6) Confidence Scoring — recusa responder se confiança abaixo de 70%. "
        "SEMPRE usar antes de enviar resposta baseada em documentos da base de conhecimento. "
        "Pitch: 'Toda resposta tem prova. Se não tem prova, sistema diz não encontro.'"
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "response_text": {
                "type": "string",
                "description": "Texto da resposta gerada pelo LLM, antes de enviar ao usuário.",
            },
            "chunks": {
                "type": "array",
                "description": "Chunks de contexto usados na resposta (document_id, title, text, score, source).",
                "items": {
                    "type": "object",
                    "properties": {
                        "document_id": {"type": "string"},
                        "title": {"type": "string"},
                        "text": {"type": "string"},
                        "score": {"type": "number"},
                        "source": {"type": "string"},
                    },
                },
            },
            "query": {
                "type": "string",
                "description": "Pergunta original do usuário (para contextualizar citações).",
            },
        },
        "required": ["response_text"],
    },
}

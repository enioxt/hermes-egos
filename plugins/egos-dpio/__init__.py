"""
egos-dpio — Qualificação interna setorial (DPIO Framework)
HERMES-FORK-007 | Status: IMPLEMENTED ✅
"""

from agent.plugins import PluginContext
from .tools import get_dpio_questions, list_supported_sectors

DPIO_QUESTIONS_SCHEMA = {
    "name": "get_dpio_questions",
    "description": (
        "Retorna perguntas DPIO adaptadas ao setor do cliente. "
        "Use para aprofundar diagnóstico de usuários internos ou coletar informações "
        "estruturadas sobre processos do cliente."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "sector": {"type": "string", "description": "Setor (ex: 'advocacia', 'dentista', 'contabilidade')"},
            "phase": {"type": "integer", "description": "Fase DPIO (0=todas, 1-5=bloco específico)", "default": 0},
        },
        "required": ["sector"],
    },
}

LIST_SECTORS_SCHEMA = {
    "name": "list_dpio_sectors",
    "description": "Lista setores suportados pelo DPIO Framework.",
    "parameters": {"type": "object", "properties": {}},
}


def register(ctx: PluginContext) -> None:
    ctx.register_tool("get_dpio_questions", get_dpio_questions, schema=DPIO_QUESTIONS_SCHEMA)
    ctx.register_tool("list_dpio_sectors", list_supported_sectors, schema=LIST_SECTORS_SCHEMA)

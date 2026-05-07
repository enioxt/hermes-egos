"""
egos-espiral — Handoff humano live (Espiral de Escuta)
HERMES-FORK-008 | Status: IMPLEMENTED ✅

Permite que o operador pause o agente e injete mensagens sem o usuário
perceber a transição. Estado persistido em ~/.hermes/profiles/<slug>/espiral/.

Aviso legal: o sistema informa que o atendimento é supervisionado por humanos
na primeira mensagem (aviso LGPD art.20 via egos-lab-chat).
"""

from agent.plugins import PluginContext
from .tools import pause_agent, resume_agent, inject_message, get_session_status

_PAUSE_SCHEMA = {
    "name": "pause_agent",
    "description": "Pausa o agente IA para uma sessão — o operador humano assume o controle.",
    "parameters": {
        "type": "object",
        "properties": {
            "session_id": {"type": "string", "description": "ID da sessão do usuário"},
            "reason": {"type": "string", "description": "Motivo do handoff (para log interno)"},
            "client_slug": {"type": "string", "description": "Slug do cliente (opcional)"},
        },
        "required": ["session_id"],
    },
}

_RESUME_SCHEMA = {
    "name": "resume_agent",
    "description": "Retoma o agente IA após handoff humano.",
    "parameters": {
        "type": "object",
        "properties": {
            "session_id": {"type": "string"},
            "client_slug": {"type": "string"},
        },
        "required": ["session_id"],
    },
}

_INJECT_SCHEMA = {
    "name": "inject_message",
    "description": "Injeta uma mensagem na sessão como se viesse do sistema, mesmo com agente pausado.",
    "parameters": {
        "type": "object",
        "properties": {
            "session_id": {"type": "string"},
            "message": {"type": "string", "description": "Mensagem a injetar"},
            "sender_label": {"type": "string", "description": "Nome do remetente (ex: 'Dra. Ana', 'Equipe')", "default": "Equipe"},
            "client_slug": {"type": "string"},
        },
        "required": ["session_id", "message"],
    },
}

_STATUS_SCHEMA = {
    "name": "get_espiral_status",
    "description": "Retorna o status da Espiral de Escuta para uma sessão (pausada? injeções?).",
    "parameters": {
        "type": "object",
        "properties": {
            "session_id": {"type": "string"},
            "client_slug": {"type": "string"},
        },
        "required": ["session_id"],
    },
}


def register(ctx: PluginContext) -> None:
    ctx.register_tool("pause_agent", pause_agent, schema=_PAUSE_SCHEMA)
    ctx.register_tool("resume_agent", resume_agent, schema=_RESUME_SCHEMA)
    ctx.register_tool("inject_message", inject_message, schema=_INJECT_SCHEMA)
    ctx.register_tool("get_espiral_status", get_session_status, schema=_STATUS_SCHEMA)

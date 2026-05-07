"""
egos-espiral — Handoff humano live (Espiral de Escuta)
HERMES-FORK-008 | Status: IMPLEMENTED ✅

Permite que o operador humano pause o agente e injete mensagens
na conversa sem o usuário perceber a transição de canal.

Estado da Espiral por sessão salvo em disco (profiles/<slug>/espiral/<session>.json).
"""

import os
import json
from datetime import datetime
from typing import Optional


def _state_path(session_id: str, client_slug: str = "") -> str:
    home = os.environ.get("HOME", "/root")
    base = f"{home}/.hermes/profiles/{client_slug}" if client_slug else f"{home}/.hermes"
    os.makedirs(f"{base}/espiral", exist_ok=True)
    return f"{base}/espiral/{session_id}.json"


def _read_state(session_id: str, client_slug: str = "") -> dict:
    path = _state_path(session_id, client_slug)
    if not os.path.exists(path):
        return {"session_id": session_id, "paused": False, "paused_at": None, "injected": []}
    with open(path) as f:
        return json.load(f)


def _write_state(session_id: str, state: dict, client_slug: str = "") -> None:
    path = _state_path(session_id, client_slug)
    with open(path, "w") as f:
        json.dump(state, f, indent=2, default=str)


def pause_agent(session_id: str, reason: str = "", client_slug: str = "") -> dict:
    """
    Pausa o agente IA para uma sessão específica.
    O operador humano assume o controle da conversa.
    O usuário não é notificado da transição (Espiral de Escuta).
    """
    state = _read_state(session_id, client_slug)
    if state.get("paused"):
        return {
            "ok": True,
            "already_paused": True,
            "paused_at": state.get("paused_at"),
            "message": f"Sessão {session_id} já está pausada.",
        }

    state["paused"] = True
    state["paused_at"] = datetime.utcnow().isoformat()
    state["pause_reason"] = reason
    _write_state(session_id, state, client_slug)

    return {
        "ok": True,
        "session_id": session_id,
        "paused": True,
        "paused_at": state["paused_at"],
        "message": (
            f"Agente pausado para sessão '{session_id}'. "
            "O operador humano agora controla a conversa. "
            "Envie mensagens normalmente — elas chegarão ao usuário como se fossem do sistema."
        ),
    }


def resume_agent(session_id: str, client_slug: str = "") -> dict:
    """Retoma o agente IA após handoff humano."""
    state = _read_state(session_id, client_slug)
    if not state.get("paused"):
        return {"ok": True, "already_active": True, "message": f"Sessão {session_id} já está ativa."}

    paused_duration = ""
    if state.get("paused_at"):
        try:
            delta = datetime.utcnow() - datetime.fromisoformat(state["paused_at"])
            paused_duration = f"{int(delta.total_seconds() / 60)}min"
        except Exception:
            pass

    state["paused"] = False
    state["resumed_at"] = datetime.utcnow().isoformat()
    _write_state(session_id, state, client_slug)

    return {
        "ok": True,
        "session_id": session_id,
        "paused": False,
        "paused_duration": paused_duration,
        "message": f"Agente IA retomado para sessão '{session_id}'. Pausado por {paused_duration}.",
    }


def inject_message(session_id: str, message: str, sender_label: str = "Equipe", client_slug: str = "") -> dict:
    """
    Injeta uma mensagem na sessão como se viesse do sistema.
    Disponível mesmo quando o agente está pausado.
    Registra no histórico de injeções para auditoria.
    """
    state = _read_state(session_id, client_slug)
    injection = {
        "ts": datetime.utcnow().isoformat(),
        "sender": sender_label,
        "message": message[:2000],  # limite de segurança
        "agent_was_paused": state.get("paused", False),
    }
    state.setdefault("injected", []).append(injection)
    _write_state(session_id, state, client_slug)

    return {
        "ok": True,
        "session_id": session_id,
        "injected": True,
        "message_preview": message[:100],
        "sender": sender_label,
        "total_injections": len(state["injected"]),
        "note": (
            "Mensagem registrada. Para enviar ao usuário final, use o canal configurado "
            "(WhatsApp/Web) para a sessão. O histórico de injeções é mantido para auditoria."
        ),
    }


def get_session_status(session_id: str, client_slug: str = "") -> dict:
    """Retorna o status atual da Espiral para uma sessão."""
    state = _read_state(session_id, client_slug)
    return {
        "ok": True,
        "session_id": session_id,
        "paused": state.get("paused", False),
        "paused_at": state.get("paused_at"),
        "resumed_at": state.get("resumed_at"),
        "total_injections": len(state.get("injected", [])),
        "last_injection": state.get("injected", [{}])[-1] if state.get("injected") else None,
    }

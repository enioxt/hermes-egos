"""
LLM Fallback automático para o hermes-egos.
Resolução do Risco R5/Gemini issue 2 (OpenRouter como SPOF).

Quando OpenRouter falha (429, 502, timeout), tenta:
  1. Google Gemini direto (GOOGLE_API_KEY)
  2. Anthropic direto (ANTHROPIC_API_KEY)
  3. Re-raise se ambos falharem

Registra o fallback no log de billing para rastreio de disponibilidade.
"""

import os
import json
import urllib.request
import urllib.error
from datetime import datetime


def _call_gemini_direct(messages: list[dict], model: str = "gemini-2.0-flash") -> str:
    """Chamar Gemini diretamente (sem OpenRouter)."""
    api_key = os.environ.get("GOOGLE_API_KEY", "")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY não configurada")

    # Converter mensagens OpenAI → Gemini format
    contents = []
    for msg in messages:
        role = "user" if msg.get("role") != "assistant" else "model"
        contents.append({"role": role, "parts": [{"text": msg.get("content", "")}]})

    payload = json.dumps({"contents": contents}).encode()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
        return data["candidates"][0]["content"]["parts"][0]["text"]


def _call_anthropic_direct(messages: list[dict], model: str = "claude-haiku-4-5-20251001") -> str:
    """Chamar Anthropic diretamente (sem OpenRouter)."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY não configurada")

    payload = json.dumps({
        "model": model,
        "max_tokens": 1024,
        "messages": messages,
    }).encode()

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
        return data["content"][0]["text"]


def call_with_fallback(
    messages: list[dict],
    primary_fn,  # callable: messages → str (o call normal do Hermes)
    client_slug: str = "",
) -> dict:
    """
    Tenta primary_fn. Se falhar com 429/502/timeout, tenta Gemini direto,
    depois Anthropic direto. Registra o fallback usado.

    Returns: {'text': str, 'provider': str, 'fallback_used': bool}
    """
    # Tentar provedor principal (OpenRouter via Hermes)
    try:
        text = primary_fn(messages)
        return {"text": text, "provider": "openrouter", "fallback_used": False}
    except Exception as primary_err:
        is_overload = any(
            code in str(primary_err)
            for code in ["429", "502", "timeout", "rate limit", "overloaded"]
        )
        if not is_overload:
            raise  # Erro real, não sobrecarga — re-raise

        _log_fallback(client_slug, "openrouter", str(primary_err))

    # Fallback 1: Gemini direto
    try:
        text = _call_gemini_direct(messages)
        _log_fallback(client_slug, "gemini_direct_success", "fallback ok")
        return {"text": text, "provider": "gemini-direct", "fallback_used": True}
    except Exception as gemini_err:
        _log_fallback(client_slug, "gemini_direct_failed", str(gemini_err))

    # Fallback 2: Anthropic direto
    try:
        text = _call_anthropic_direct(messages)
        _log_fallback(client_slug, "anthropic_direct_success", "fallback ok")
        return {"text": text, "provider": "anthropic-direct", "fallback_used": True}
    except Exception as anthropic_err:
        _log_fallback(client_slug, "anthropic_direct_failed", str(anthropic_err))
        raise RuntimeError(
            f"Todos os provedores LLM falharam. OpenRouter: {primary_err}. "
            f"Gemini: {gemini_err}. Anthropic: {anthropic_err}."
        ) from anthropic_err


def _log_fallback(client_slug: str, event: str, detail: str) -> None:
    """Log simples de eventos de fallback para rastreio de disponibilidade."""
    home = os.environ.get("HOME", "/root")
    log_path = f"{home}/.hermes/profiles/{client_slug}/llm-fallback.jsonl" if client_slug else f"{home}/.egos/llm-fallback.jsonl"
    try:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        entry = json.dumps({
            "ts": datetime.utcnow().isoformat(),
            "client": client_slug,
            "event": event,
            "detail": detail[:200],
        })
        with open(log_path, "a") as f:
            f.write(entry + "\n")
    except Exception:
        pass  # log failure não deve quebrar o agente

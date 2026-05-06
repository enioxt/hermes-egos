"""Implementação das tools de billing do egos-billing."""

import os
import json
import urllib.request
from datetime import datetime


def _get_openrouter_usage() -> dict:
    """Consulta GET /api/v1/key no OpenRouter e retorna dados de uso."""
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY não configurada para este cliente")

    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/key",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())["data"]


def _send_telegram_alert(message: str) -> None:
    """Envia alerta via Telegram para o operador EGOS."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        return  # silencioso se não configurado

    payload = json.dumps({
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
    }).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass  # falha de notificação não deve quebrar o agente


def check_usage(client_slug: str = "") -> dict:
    """
    Verifica uso OpenRouter do cliente.
    Dispara alertas Telegram se >= 80% do limite.
    """
    try:
        data = _get_openrouter_usage()
    except Exception as e:
        return {"ok": False, "error": str(e)}

    usage_monthly = data.get("usage_monthly", 0)
    limit = data.get("limit")
    limit_remaining = data.get("limit_remaining")
    label = data.get("label", client_slug or "cliente")

    # Calcular percentual
    if limit and limit > 0:
        pct = (usage_monthly / limit) * 100
    else:
        pct = 0.0

    # Custo estimado em BRL (1 crédito OpenRouter ≈ $1 USD ≈ R$5.80)
    cost_usd = usage_monthly / 1000  # OpenRouter usa microdólares
    cost_brl = cost_usd * 5.8

    result = {
        "ok": True,
        "client": label,
        "usage_monthly_credits": usage_monthly,
        "limit_credits": limit,
        "limit_remaining": limit_remaining,
        "percent_used": round(pct, 1),
        "cost_usd": round(cost_usd, 4),
        "cost_brl": round(cost_brl, 2),
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Alertas automáticos
    budget_brl = float(os.environ.get("CLIENT_BUDGET_BRL", "500"))
    client_wa = os.environ.get("CLIENT_WA_NUMBER", "")

    if pct >= 100:
        msg = (
            f"🚨 *LIMITE ATINGIDO* — {label}\n"
            f"Uso: {pct:.0f}% do limite OpenRouter\n"
            f"Custo: R${cost_brl:.2f}\n"
            f"Agente PAUSADO automaticamente pelo OpenRouter.\n"
            f"Contate o cliente para upgrade ou aguarde renovação."
        )
        _send_telegram_alert(msg)
        result["alert"] = "LIMIT_REACHED"

    elif pct >= 80:
        msg = (
            f"⚠️ *80% DO LIMITE* — {label}\n"
            f"Uso: {pct:.0f}% | Custo: R${cost_brl:.2f}\n"
            f"Restante: {limit_remaining} créditos\n"
            f"Considere upgrade de plano."
        )
        _send_telegram_alert(msg)
        result["alert"] = "WARNING_80PCT"

    return result


def get_usage_report(period: str = "monthly") -> dict:
    """Gera relatório de uso por período."""
    try:
        data = _get_openrouter_usage()
    except Exception as e:
        return {"ok": False, "error": str(e)}

    field_map = {
        "daily": "usage_daily",
        "weekly": "usage_weekly",
        "monthly": "usage_monthly",
    }
    field = field_map.get(period, "usage_monthly")
    usage = data.get(field, 0)
    cost_usd = usage / 1000
    cost_brl = cost_usd * 5.8

    return {
        "ok": True,
        "period": period,
        "usage_credits": usage,
        "cost_usd": round(cost_usd, 4),
        "cost_brl": round(cost_brl, 2),
        "label": data.get("label", "cliente"),
        "timestamp": datetime.utcnow().isoformat(),
    }

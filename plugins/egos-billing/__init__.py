"""
egos-billing — OpenRouter per-client usage tracker
HERMES-FORK-004 | Status: IMPLEMENTED ✅

Monitora uso de LLM por cliente via OpenRouter API:
- GET /api/v1/key retorna usage_monthly, limit_remaining
- Alerta Telegram quando >= 80% do orçamento
- Hard limit via credit_limit da chave OpenRouter (kicka em 100%)

Env vars necessárias:
  OPENROUTER_API_KEY      — chave do cliente (1 por cliente, com credit_limit)
  TELEGRAM_BOT_TOKEN      — bot EGOS para alertas operacionais
  TELEGRAM_CHAT_ID        — chat do Enio (171767219)
  CLIENT_BUDGET_BRL       — orçamento mensal em BRL (default: 500)
  CLIENT_WA_NUMBER        — número WhatsApp do cliente (opcional)
"""

from agent.plugins import PluginContext
from .schemas import CHECK_USAGE_SCHEMA, GET_USAGE_REPORT_SCHEMA
from .tools import check_usage, get_usage_report


def register(ctx: PluginContext) -> None:
    ctx.register_tool("check_billing_usage", check_usage, schema=CHECK_USAGE_SCHEMA)
    ctx.register_tool("get_usage_report", get_usage_report, schema=GET_USAGE_REPORT_SCHEMA)

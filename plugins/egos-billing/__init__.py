"""
egos-billing — OpenRouter per-client usage tracker
HERMES-FORK-004 | Status: in_development

Monitora uso de LLM por cliente via OpenRouter API:
- GET /api/v1/key retorna usage_monthly, limit_remaining
- Alerta Telegram quando >= 80% do orçamento
- Alerta WhatsApp cliente quando >= 80%
- Hard limit via credit_limit da chave OpenRouter (kicka automaticamente em 100%)

Roda como cron interno do Hermes (1x/hora).
"""

from agent.plugins import PluginContext


def register(ctx: PluginContext) -> None:
    # TODO: implementar em HERMES-FORK-004
    # ctx.register_tool("check_billing_usage", check_usage)
    # ctx.register_tool("get_usage_report", get_usage_report)
    raise NotImplementedError("egos-billing: NOT IMPLEMENTED — see HERMES-FORK-004 in egos/TASKS.md")

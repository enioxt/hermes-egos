"""Schemas para as tools do egos-billing (o que o LLM vê)."""

CHECK_USAGE_SCHEMA = {
    "name": "check_billing_usage",
    "description": (
        "Verifica o uso de LLM do cliente via OpenRouter. "
        "Retorna usage_monthly, limit_remaining, percentual usado, e alerta se >= 80%."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "client_slug": {
                "type": "string",
                "description": "Identificador do cliente (ex: 'advocacia-dr-joao'). Opcional se rodando no profile do cliente.",
            }
        },
        "required": [],
    },
}

GET_USAGE_REPORT_SCHEMA = {
    "name": "get_usage_report",
    "description": "Gera relatório detalhado de uso de LLM do cliente: diário, semanal, mensal, custo estimado em BRL.",
    "parameters": {
        "type": "object",
        "properties": {
            "period": {
                "type": "string",
                "enum": ["daily", "weekly", "monthly"],
                "description": "Período do relatório",
            }
        },
        "required": ["period"],
    },
}

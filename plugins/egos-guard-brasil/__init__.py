"""
egos-guard-brasil — PII masking LGPD para respostas do agente
HERMES-FORK-005 | Status: IMPLEMENTED ✅

Port de packages/guard-brasil/src/ (EGOS kernel TypeScript → Python).

Detecta e mascara:
  CPF, CNPJ, RG, Telefone, E-mail, CEP, Placa (antiga + Mercosul),
  MASP, REDS, e outros identificadores brasileiros.

Aplicado como hook pós-geração em todas as respostas do agente cliente.
Conformidade: Lei 13.709/2018 (LGPD).

Env vars: nenhuma obrigatória (funciona offline).
"""

from agent.plugins import PluginContext
from .schemas import CHECK_PII_SCHEMA, SCAN_PII_SCHEMA
from .tools import check_response_for_pii, scan_pii


def _scan_text_for_pii(text: str) -> dict:
    """Wrapper para uso como tool (retorna dict serializable)."""
    matches = scan_pii(text)
    return {
        "ok": True,
        "pii_detected": len(matches) > 0,
        "pii_count": len(matches),
        "findings": [
            {
                "pattern_id": m.pattern_id,
                "label": m.label,
                "matched_preview": m.matched[:4] + "***",  # não expõe o valor completo
                "confidence": m.confidence,
            }
            for m in matches
        ],
    }


def register(ctx: PluginContext) -> None:
    ctx.register_tool("check_response_for_pii", check_response_for_pii, schema=CHECK_PII_SCHEMA)
    ctx.register_tool("scan_text_for_pii", _scan_text_for_pii, schema=SCAN_PII_SCHEMA)

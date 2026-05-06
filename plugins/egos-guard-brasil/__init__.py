"""
egos-guard-brasil — PII masking LGPD
HERMES-FORK-005 | Status: in_development

Port do packages/guard-brasil (TypeScript → Python).
Detecta e mascara: CPF, CNPJ, RG, MASP, telefone, endereço, placa, e-mail.
Aplicado como hook pós-geração em todas as respostas.
"""

from agent.plugins import PluginContext


def register(ctx: PluginContext) -> None:
    # TODO: implementar em HERMES-FORK-005
    raise NotImplementedError("egos-guard-brasil: NOT IMPLEMENTED — see HERMES-FORK-005 in egos/TASKS.md")

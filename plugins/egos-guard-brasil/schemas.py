"""Schemas das tools egos-guard-brasil para o LLM."""

CHECK_PII_SCHEMA = {
    "name": "check_response_for_pii",
    "description": (
        "Verifica se um texto contém dados pessoais (PII) brasileiros e os mascara. "
        "Detecta: CPF, CNPJ, RG, telefone, e-mail, CEP, placa, MASP, REDS. "
        "Aplica mascaramento conforme LGPD (Lei 13.709/2018). "
        "Usar antes de enviar qualquer resposta que possa conter dados do usuário."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "response_text": {
                "type": "string",
                "description": "Texto da resposta a ser verificado e possivelmente mascarado.",
            }
        },
        "required": ["response_text"],
    },
}

SCAN_PII_SCHEMA = {
    "name": "scan_text_for_pii",
    "description": (
        "Escaneia um texto e lista todos os dados pessoais encontrados, sem mascarar. "
        "Útil para auditoria e para informar o usuário sobre quais dados foram detectados."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "Texto a ser escaneado em busca de PII.",
            }
        },
        "required": ["text"],
    },
}

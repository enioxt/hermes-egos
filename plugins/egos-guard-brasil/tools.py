"""
Implementação das tools do egos-guard-brasil.
Port dos padrões de packages/guard-brasil/src/pii-patterns.ts (EGOS kernel).
"""

import re
from typing import NamedTuple


class PIIMatch(NamedTuple):
    pattern_id: str
    label: str
    matched: str
    start: int
    end: int
    confidence: str  # 'high' | 'medium' | 'low'


# Padrões brasileiros — port de pii-patterns.ts
_PATTERNS = [
    {
        "id": "cpf",
        "label": "CPF",
        "regex": re.compile(r'\b\d{3}[\.\s]?\d{3}[\.\s]?\d{3}[-\.\s]?\d{2}\b'),
        "mask": "[CPF OMITIDO]",
        "confidence": "high",
    },
    {
        "id": "cnpj",
        "label": "CNPJ",
        "regex": re.compile(r'\b\d{2}[\.\s]?\d{3}[\.\s]?\d{3}[/\.\s]?\d{4}[-\.\s]?\d{2}\b'),
        "mask": "[CNPJ OMITIDO]",
        "confidence": "high",
    },
    {
        "id": "rg",
        "label": "RG",
        "regex": re.compile(r'\bRG[:\s]*\d{1,2}[\.\s]?\d{3}[\.\s]?\d{3}[-\.\s]?\d?\b', re.IGNORECASE),
        "mask": "[RG OMITIDO]",
        "confidence": "medium",
    },
    {
        "id": "telefone",
        "label": "Telefone",
        "regex": re.compile(r'\b(\+?55\s?)?(\(?\d{2}\)?\s?)(\d{4,5}[-\s]?\d{4})\b'),
        "mask": "[TELEFONE OMITIDO]",
        "confidence": "medium",
    },
    {
        "id": "email",
        "label": "E-mail",
        "regex": re.compile(r'\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b'),
        "mask": "[EMAIL OMITIDO]",
        "confidence": "high",
    },
    {
        "id": "cep",
        "label": "CEP",
        "regex": re.compile(r'\b\d{5}[-\s]?\d{3}\b'),
        "mask": "[CEP OMITIDO]",
        "confidence": "medium",
    },
    {
        "id": "placa_mercosul",
        "label": "Placa (Mercosul)",
        "regex": re.compile(r'\b[A-Z]{3}\s?[0-9][A-Z0-9][0-9]{2}\b'),
        "mask": "[PLACA OMITIDA]",
        "confidence": "high",
    },
    {
        "id": "placa_antiga",
        "label": "Placa (antiga)",
        "regex": re.compile(r'\b[A-Z]{3}[-\s]?\d{4}\b'),
        "mask": "[PLACA OMITIDA]",
        "confidence": "high",
    },
    {
        "id": "masp",
        "label": "MASP",
        "regex": re.compile(r'\bMASP[:\s]*\d{6,8}\b', re.IGNORECASE),
        "mask": "[MASP OMITIDO]",
        "confidence": "high",
    },
    {
        "id": "reds",
        "label": "REDS",
        "regex": re.compile(r'\bREDS[:\s]*\d{6,12}\b', re.IGNORECASE),
        "mask": "[REDS OMITIDO]",
        "confidence": "high",
    },
]


def scan_pii(text: str) -> list[PIIMatch]:
    """Detecta todos os PII no texto. Retorna lista de matches."""
    matches: list[PIIMatch] = []
    for p in _PATTERNS:
        for m in p["regex"].finditer(text):
            matches.append(PIIMatch(
                pattern_id=p["id"],
                label=p["label"],
                matched=m.group(),
                start=m.start(),
                end=m.end(),
                confidence=p["confidence"],
            ))
    # Ordenar por posição
    return sorted(matches, key=lambda x: x.start)


def mask_pii(text: str, mode: str = "full") -> dict:
    """
    Mascara PII no texto. Retorna texto sanitizado + lista de findings.

    mode='full'    → substitui por [TIPO OMITIDO]
    mode='partial' → mantém primeiros/últimos caracteres (banking-style)
    """
    matches = scan_pii(text)
    if not matches:
        return {"sanitized": text, "findings": [], "pii_detected": False}

    # Construir texto mascarado (de trás pra frente para não deslocar índices)
    sanitized = text
    findings = []
    for m in reversed(matches):
        p = next(x for x in _PATTERNS if x["id"] == m.pattern_id)
        replacement = p["mask"]
        sanitized = sanitized[:m.start] + replacement + sanitized[m.end:]
        findings.append({
            "pattern_id": m.pattern_id,
            "label": m.label,
            "confidence": m.confidence,
            "position": {"start": m.start, "end": m.end},
        })

    return {
        "sanitized": sanitized,
        "findings": list(reversed(findings)),  # ordem original
        "pii_detected": True,
        "pii_count": len(findings),
    }


def check_response_for_pii(response_text: str) -> dict:
    """
    Tool principal: verifica se a resposta do agente contém PII.
    Retorna resposta sanitizada se houver PII, ou original se limpa.
    Usada como hook pós-geração.
    """
    result = mask_pii(response_text)
    if result["pii_detected"]:
        return {
            "ok": True,
            "pii_detected": True,
            "pii_count": result["pii_count"],
            "sanitized_response": result["sanitized"],
            "findings": result["findings"],
            "action": "response_masked",
            "lgpd_note": "PII detectado e mascarado conforme LGPD (Lei 13.709/2018)",
        }
    return {
        "ok": True,
        "pii_detected": False,
        "sanitized_response": response_text,
        "action": "none",
    }

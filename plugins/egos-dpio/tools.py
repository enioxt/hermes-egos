"""
egos-dpio — Qualificação interna setorial via DPIO Framework
HERMES-FORK-007 | Status: IMPLEMENTED ✅

Carrega perguntas DPIO setoriais dos arquivos em egos/docs/guides/dpio/
e fornece ao agente do cliente. Diferente do DPIO de aquisição (egos-lab-chat):
este qualifica usuários internos, não leads externos.

Setores suportados: advocacia, agronomia, clinica-especialidade, comercio,
contabilidade, dentista, policia-seguranca, saude-administrativa
"""

import os
import re
from functools import lru_cache


# Mapeamento setor → arquivo DPIO
SECTOR_MAP = {
    "advocacia": "advocacia.md",
    "juridico": "advocacia.md",
    "advogado": "advocacia.md",
    "agronegocio": "agronomia.md",
    "agricultor": "agronomia.md",
    "agronomo": "agronomia.md",
    "clinica": "clinica-especialidade.md",
    "fisioterapia": "clinica-especialidade.md",
    "nutricao": "clinica-especialidade.md",
    "psicologia": "clinica-especialidade.md",
    "comercio": "comercio.md",
    "loja": "comercio.md",
    "varejo": "comercio.md",
    "contabilidade": "contabilidade.md",
    "contador": "contabilidade.md",
    "contabil": "contabilidade.md",
    "dentista": "dentista.md",
    "odonto": "dentista.md",
    "policia": "policia-seguranca.md",
    "seguranca": "policia-seguranca.md",
    "saude": "saude-administrativa.md",
    "hospital": "saude-administrativa.md",
    "clinica-medica": "saude-administrativa.md",
}

def _get_dpio_dir() -> str:
    """Retorna o diretório base dos arquivos DPIO."""
    # Primeiro tenta variável de ambiente
    env_dir = os.environ.get("EGOS_DPIO_DIR", "")
    if env_dir and os.path.isdir(env_dir):
        return env_dir
    # Fallback: path relativo ao hermes-egos
    candidate = "/home/enio/egos/docs/guides/dpio"
    if os.path.isdir(candidate):
        return candidate
    return ""


@lru_cache(maxsize=16)
def _load_dpio_file(filename: str) -> str:
    """Carrega arquivo DPIO com cache em memória."""
    dpio_dir = _get_dpio_dir()
    if not dpio_dir:
        return ""
    path = os.path.join(dpio_dir, filename)
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8") as f:
        return f.read()


def get_dpio_questions(sector: str, phase: int = 0) -> dict:
    """
    Retorna perguntas DPIO setoriais para o setor e fase especificados.

    sector: string identificando o setor (ex: "advocacia", "dentista")
    phase: 0=todas, 1=diagnóstico inicial, 2=dados, 3=dores, 4=digital, 5=decisores

    Returns: {'ok': bool, 'sector': str, 'phase': int, 'questions': str, 'filename': str}
    """
    # Normalizar setor
    sector_lower = sector.lower().strip()
    filename = SECTOR_MAP.get(sector_lower, "")

    # Busca parcial se não encontrou exato
    if not filename:
        for key, val in SECTOR_MAP.items():
            if key in sector_lower or sector_lower in key:
                filename = val
                break

    if not filename:
        return {
            "ok": False,
            "sector": sector,
            "error": f"Setor '{sector}' não mapeado. Disponíveis: {', '.join(set(SECTOR_MAP.values()))}",
            "questions": "",
        }

    content = _load_dpio_file(filename)
    if not content:
        return {
            "ok": False,
            "sector": sector,
            "error": f"Arquivo DPIO '{filename}' não encontrado.",
            "questions": "",
        }

    # Filtrar por fase se especificado
    if phase > 0:
        # Extrair blocos por fase
        phase_labels = {
            1: "Bloco A", 2: "Bloco B", 3: "Bloco C",
            4: "Bloco D", 5: "Bloco E",
        }
        label = phase_labels.get(phase, "")
        if label:
            pattern = rf"### {re.escape(label)}[^\n]*\n(.*?)(?=###|\Z)"
            match = re.search(pattern, content, re.DOTALL)
            content = match.group(0) if match else content

    return {
        "ok": True,
        "sector": sector,
        "phase": phase,
        "questions": content[:3000],  # limitar tamanho
        "filename": filename,
        "note": "Use estas perguntas adaptadas ao setor para aprofundar o diagnóstico do cliente.",
    }


def list_supported_sectors() -> dict:
    """Lista setores suportados pelo DPIO."""
    unique = list(dict.fromkeys(SECTOR_MAP.values()))
    return {
        "ok": True,
        "sectors": list(set(SECTOR_MAP.keys())),
        "files": unique,
        "count": len(unique),
    }

# EGOS Fork Guide — hermes-egos

> **Fork de:** [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) (MIT)
> **Mantenedor:** [enioxt](https://github.com/enioxt) — EGOS Lab, Patos de Minas, MG
> **Propósito:** Motor operacional da [Central EGOS](https://lab.egos.ia.br) — IA governada para PMEs brasileiras

---

## Arquitetura do Fork (Padrão PAI)

**Regra fundamental: nunca modificar arquivos do core de Hermes.**

Todo código EGOS vive em diretórios novos:

```
hermes-egos/
├── plugins/                      ← EGOS (novos arquivos)
│   ├── egos-billing/             # OpenRouter per-client usage tracker
│   ├── egos-guard-brasil/        # PII masking LGPD (CPF, CNPJ, RG, etc.)
│   ├── egos-anti-hallucination/  # 7 técnicas anti-alucinação
│   ├── egos-dpio/                # Qualificação interna por vertical
│   ├── egos-espiral/             # Handoff humano live (pause/inject)
│   └── egos-kb-tools/            # Busca KB cliente via match_kb_hybrid
├── skills/
│   └── egos-personas/            # 8 personas setoriais BR (advocacia, dentista, etc.)
├── profiles-templates/           # Templates de provisionamento por tier
│   ├── solo/                     # hermes -p <cliente> na VPS EGOS
│   ├── pro/                      # Docker container dedicado
│   └── enterprise/               # VPS do próprio cliente
├── upstream-monitor/             # Diffs categorizados gerados pelo CI
├── .github/workflows/
│   └── upstream-sync.yml         # Cron diário de monitoramento de upstream
├── EGOS-FORK-GUIDE.md            # Este arquivo
└── (todo o resto = core Hermes, intocado)
```

Referência do padrão: [PAI Issue #128](https://github.com/danielmiessler/Personal_AI_Infrastructure/issues/128)

---

## Remotes

| Remote | URL | Propósito |
|--------|-----|-----------|
| `origin` | `git@github.com:enioxt/hermes-egos.git` | Nosso fork |
| `upstream` | `https://github.com/NousResearch/hermes-agent.git` | Hermes source |

```bash
# Configurar remotes (já feito no clone)
git remote add upstream https://github.com/NousResearch/hermes-agent.git
git fetch upstream
```

---

## Política de Sync com Upstream

### Categorias de commit

| Categoria | Critério | Ação |
|-----------|----------|------|
| 🔴 SECURITY | CVE, vuln fix, auth | Merge em <48h obrigatório |
| 🟢 BUGFIX | Fix de comportamento | Merge no próximo sprint semanal |
| 🟡 FEATURE | Nova funcionalidade | Avaliar se útil para clientes Central EGOS |
| ⚪ IRRELEVANTE | Adapters não usados (ex: Yuanbao) | Ignorar |
| 🚨 BREAKING | Quebra de API pública | Planejar rollout, avisar clientes 7d antes |

### Processo de sync

```bash
# 1. Verificar diff com upstream (automático via CI, ou manual)
git fetch upstream
git log origin/main..upstream/main --oneline

# 2. Categorizar commits (o GitHub Action faz isso automaticamente)

# 3. Se SECURITY → merge imediato:
git rebase upstream/main
# Resolver conflitos: sempre adaptar nosso código ao padrão upstream
# Nunca preservar padrão antigo — adaptar egos-* ao novo padrão do core

# 4. Push
git push origin main
```

### Resolução de conflitos

Quando rebasing e conflitos ocorrem em arquivos EGOS:
- **Nossos novos arquivos (plugins/, skills/, etc.)**: sempre manter nossa versão (`git add <file>`)
- **Conflito em arquivo core**: sempre aceitar versão upstream, então re-adaptar nosso plugin se necessário
- **README.md**: manter nossa versão (tem contexto EGOS)

---

## Desenvolver um Plugin

```
plugins/egos-billing/
├── plugin.yaml      # Metadados do plugin
├── __init__.py      # Registro (register() function)
├── schemas.py       # Tool schemas para o LLM
└── tools.py         # Implementação das ferramentas
```

### plugin.yaml mínimo

```yaml
name: egos-billing
version: 0.1.0
description: OpenRouter per-client usage tracker com alertas 80/100%
author: enioxt
requires_env:
  - OPENROUTER_API_KEY
  - TELEGRAM_BOT_TOKEN
  - TELEGRAM_CHAT_ID
```

### __init__.py mínimo

```python
from agent.plugins import PluginContext

def register(ctx: PluginContext):
    from .tools import check_usage
    ctx.register_tool("check_billing_usage", check_usage)
```

Instalar para desenvolvimento:
```bash
# Link o plugin para o diretório de plugins do Hermes
ln -s $(pwd)/plugins/egos-billing ~/.hermes/plugins/egos-billing
# Ou instalar via pip com entry_point (produção)
```

---

## Provisionamento de Cliente (Profiles)

Cada cliente da Central EGOS recebe um profile Hermes isolado:

```bash
# Tier Solo — na VPS EGOS
hermes -p advocacia-dr-joao setup
# → cria ~/.hermes/profiles/advocacia-dr-joao/ com config, memory, sessions isolados

# Tier Pro — Docker container dedicado
docker run -v /opt/hermes-clients/clinica-xyz:/root/.hermes \
  enioxt/hermes-egos -p clinica-xyz

# Tier Enterprise — VPS do cliente (via SSH)
ssh cliente-vps
hermes -p empresa-abc setup
```

Template de configuração por tier: `profiles-templates/{solo,pro,enterprise}/config.yaml`

---

## Transparência com Clientes

Quando perguntado sobre o motor:

> "Central EGOS é implementado sobre o Hermes Agent (Nous Research, open-source MIT, 103k stars).
> Customizamos com Guard Brasil (LGPD), setorização para o mercado brasileiro, anti-alucinação
> comprovada e monitoramento de custos por cliente. Você tem acesso ao motor e aos seus dados."

---

## Pre-commit no Kernel EGOS

O kernel `/home/enio/egos` tem um hook que alerta quando o fork está desatualizado:

```bash
# .husky/_checks/09-hermes-upstream.sh
# warn se >14 dias sem sync, block se >30 dias
```

---

## Links

- **Upstream:** https://github.com/NousResearch/hermes-agent
- **Central EGOS:** https://lab.egos.ia.br
- **Decisão de arquitetura:** `egos/docs/governance/HERMES_EGOS_FORK_DECISION.md`
- **Tasks:** `egos/TASKS.md §HERMES-EGOS FORK`

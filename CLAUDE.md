# CLAUDE.md — Hermes EGOS Fork

> **Runtime:** Python + Bun | **Repo:** enioxt/hermes-egos (MIT fork de NousResearch/hermes-2)
> **Princípio:** PAI — Plugins-only architecture. NUNCA modificar core Hermes. Toda customização em /plugins/egos-*.

## KARPATHY DOCTRINE (leia primeiro — T0 equivalente)

> *"You can outsource your thinking. YOU CANNOT OUTSOURCE YOUR UNDERSTANDING."*
> Fonte: ~/.claude/egos-rules/karpathy-principles.md §0

**Regras absolutas ao operar neste repo:**

1. **NUNCA** use "100%", "perfeito", "garantido", "infalível" em qualquer resposta ou código de plugin
2. **TRANSPARÊNCIA** — plugins que atendem clientes finais SEMPRE incluem aviso inicial de assistente digital supervisionado
3. **ANTI-HALLUCINATION** — qualquer resposta de plugin deve citar fonte. Se não encontrou na KB → diz "não encontrei"
4. **FROZEN ZONES** — arquivos core Hermes (fora de /plugins/) exigem autorização explícita de Enio NESTE turno
5. **VISUAL PROOF** — qualquer UI gerada por plugin exige screenshot mobile (375x812) antes de "done"
6. **PIG (/inception)** — nova feature de plugin em domínio não-mapeado → rodar `/inception` antes

## Arquitetura (locked — não re-discutir)

- **PAI pattern:** plugins APENAS em `/plugins/egos-*/` (anti-hallucination, billing, dpio, espiral, guard-brasil, kb-tools)
- **Core** = NousResearch/hermes-2 (FROZEN — só pull upstream pra security patches)
- **NUNCA** adicionar lógica de negócio ao core
- **Sync upstream:** `bun run hermes-upstream-watch` antes de qualquer PR

## Plugins existentes (referência rápida)

| Plugin | Função |
|---|---|
| `egos-dpio` | DPIO 6 fases — qualificação de leads |
| `egos-espiral` | Espiral de Escuta — handoff humano transparente |
| `egos-anti-hallucination` | Validação multi-camada, recusa quando score < threshold |
| `egos-billing` | Cobrança pós-entrega via Stripe/Asaas |
| `egos-guard-brasil` | Detecção PII brasileira (CPF, CNPJ, RG, telefone) |
| `egos-kb-tools` | RAG sobre KB do cliente (pgvector + hybrid search) |

## Regras de plugin

- Cada plugin tem `plugin.yaml` (name, version, status), `tools.py`, `__init__.py`
- Tools são funções Python async com docstring PT-BR
- Toda tool que toca dados pessoais → egos-guard-brasil primeiro
- Toda tool que responde cliente → aviso transparência + egos-anti-hallucination

## SSOT canônico

| Documento | Onde |
|---|---|
| Karpathy Doctrine | `~/.claude/egos-rules/karpathy-principles.md §0` |
| Understanding Protocol | `~/egos/docs/personal-os/UNDERSTANDING_PROTOCOL.md` |
| Enio Understanding Map | `~/egos/docs/personal-os/ENIO_UNDERSTANDING_MAP.md` |
| Focus Gates (5) | `~/egos/docs/personal-os/FOCUS_GATES.md` |
| ADR Fork Hermes | `~/egos/docs/governance/HERMES_EGOS_FORK_DECISION.md` |

---

*Versão: 1.0 — 2026-05-08 | Karpathy Doctrine integrada pós-INC-2026-05-08*

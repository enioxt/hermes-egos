# UPSTREAM_KANBAN_AUDIT — Hermes Kanban v0.12 Audit

> **Auditado em:** 2026-05-06 | **Por:** GROK-KBN-001
> **Ref:** HARVEST.md P88, docs/strategy/CHATGROK_INTEGRATION_PLAN.md §7

## Conclusão principal

**O Kanban já está implementado neste fork.** Não é necessário portar do upstream — está operacional em Python (SQLite-backed).

---

## Features presentes neste fork (verificado)

| Feature | Status | Localização |
|---------|--------|-------------|
| Task claiming (exclusive, atomic) | ✅ | `hermes_cli/kanban_db.py` |
| Heartbeat (runaway prevention) | ✅ | `last_heartbeat_at` field + `heartbeat_claim()` |
| SQLite durable state | ✅ | `~/.hermes/kanban.db` (per-board) |
| Multi-board isolation | ✅ | Board slug separation |
| Task status machine | ✅ | `todo → ready → running → blocked → done → archived` |
| Comments per task (humans + agents) | ✅ | `task_comments` table |
| Task links (parent-child) | ✅ | `task_links` table |
| Workspaces (shared file handoff) | ✅ | `workspaces_root()` |
| Worker logs per run | ✅ | `worker_logs_dir()` |
| Dashboard | ✅ | `plugins/kanban/dashboard/` |
| Systemd service | ✅ | `plugins/kanban/systemd/` |
| Python tools for agent tool-calls | ✅ | `tools/kanban_tools.py` |
| `hermes kanban` CLI (15 verbs) | ✅ | `hermes_cli/kanban.py` |

---

## Comparação com o que @NousResearch anunciou em v0.12.0

| Feature anunciada | Nosso fork |
|---|---|
| Multi-agent via Kanban | ✅ `kanban_tools.py` registrado sob `HERMES_KANBAN_TASK` |
| Task claiming sem double-claim | ✅ Atomic SQLite claim |
| Heartbeats + runtime caps | ✅ `last_heartbeat_at`, capped in dispatcher |
| Shared workspaces | ✅ `workspaces_root()` por board |
| Comments per task | ✅ `task_comments` table |
| Durable (SQLite-backed) | ✅ `kanban.db` sobrevive a restarts |
| Live dashboard | ✅ `plugins/kanban/dashboard/` |
| Domain skills por task | ⚠️ Skills são globais — profile específico por task não implementado |
| No double-claims (race condition) | ✅ SQLite exclusive write |
| Project isolation | ✅ Multi-board por slug |

---

## Decisão: native vs plugin adapter

**Resultado:** Native (zero código adicional necessário).

O Kanban já funciona out-of-the-box para:
1. Multi-agent orchestration via `HERMES_KANBAN_TASK` env var
2. Task claiming atômico (SQLite)
3. Handoff via workspaces

**O que falta para Central EGOS:**
- Profile-pinning por task domain (GROK-KBN-004, P2)
- Integração com vault — quando task completa com evidência, capturar no vault

---

## Como usar no Central EGOS

```bash
# Criar board para cliente
hermes kanban init --board <slug-cliente>

# Worker agent roda como:
HERMES_KANBAN_TASK=<task_id> hermes chat

# Ver board ao vivo
hermes dashboard --board <slug-cliente>
```

**Tier recomendado:** Pro e Enterprise (Solo usa Hermes direto sem Kanban por padrão).

---

## Links internos

- `hermes_cli/kanban.py` — CLI 15 verbos
- `hermes_cli/kanban_db.py` — SQLite layer
- `tools/kanban_tools.py` — Tool-call surface para agents
- `plugins/kanban/dashboard/` — Web dashboard

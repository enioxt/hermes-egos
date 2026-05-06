# hermes-egos — Motor da Central EGOS

> Fork de [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) (MIT)
> customizado para o mercado brasileiro com plugins LGPD, anti-alucinação e setorização.

Este repositório é o **runtime do agente operacional** da [Central EGOS](https://lab.egos.ia.br) —
plataforma de IA governada para profissionais liberais e PMEs brasileiras.

## O que está aqui

```
plugins/egos-billing/          → OpenRouter per-client usage tracking + alertas
plugins/egos-guard-brasil/     → PII masking LGPD (CPF, CNPJ, RG, endereço, etc.)
plugins/egos-anti-hallucination/ → 7 técnicas comprovadas: provenance, eval, RAG compression...
plugins/egos-dpio/             → Qualificação por vertical (advocacia, saúde, contábil...)
plugins/egos-espiral/          → Handoff humano ao vivo (pause IA → injeta mensagem → retoma)
plugins/egos-kb-tools/         → Busca na base de conhecimento do cliente
skills/egos-personas/          → 8 personas setoriais BR
profiles-templates/            → Configuração por tier (Solo/Pro/Enterprise)
```

## Como é usado

```
Aquisição:   lab.egos.ia.br/chat → chatbot DPIO (egos-lab-chat)
                    ↓ contrato fechado
Implantação: /central-egos-provision → /central-egos-ingest → /central-egos-canais
                    ↓
Operação:    hermes-egos (este fork) na VPS — perfil por cliente, plugins ativos
```

## Diferencial

> "Toda resposta tem prova. Você clica e vê o documento original.
> Se não tem prova, o sistema diz 'não encontro'."

7 técnicas anti-alucinação implementadas em produção. Ver `ANTI_HALLUCINATION_COMPLETE_GUIDE.md`.

## Para desenvolvedores

- Nunca modificar arquivos do core Hermes — ver `EGOS-FORK-GUIDE.md`
- Sync com upstream via GitHub Action (`.github/workflows/upstream-sync.yml`)
- Documentação original: ver `README.md` (Nous Research)

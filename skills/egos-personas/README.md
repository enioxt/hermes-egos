# EGOS Personas Setoriais

8 personas para o mercado brasileiro. Carregadas pelo Hermes quando o setor do cliente é detectado.

| Arquivo | Vertical | Persona |
|---|---|---|
| `advocacia.md` | Jurídico | Advogados, escritórios OAB |
| `agronegocio.md` | Agronegócio | Produtores, cooperativas, agrônomos |
| `clinica-especialidade.md` | Saúde | Fisio, nutrição, psicologia, fonoaudiologia |
| `comercio.md` | Comércio | Lojas, e-commerce, varejo |
| `contabilidade.md` | Contábil | Contadores, escritórios CRC |
| `dentista.md` | Odontologia | Consultórios, clínicas odontológicas |
| `educacao.md` | Educação | Escolas, cursos, EAD |
| `veterinario.md` | Saúde Animal | Clínicas vet, pet shops |

## Como usar no Hermes

```python
# No plugin egos-dpio ou egos-kb-tools:
skill_path = f"skills/egos-personas/{sector}.md"
persona_content = open(skill_path).read()
# Injetar no system prompt do perfil do cliente
```

## Origem

Fonte: `egos/docs/skills/personas/*/SKILL.md` (EGOS kernel).
Sincronizar quando personas forem atualizadas no kernel.

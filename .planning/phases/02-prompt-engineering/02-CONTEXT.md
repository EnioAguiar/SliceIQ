# Phase 2: Prompt Engineering - Context

**Gathered:** 2026-05-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Melhorar precisão dos prompts LLM para que IA respeite duration_min/max e escolha timestamps corretos. Phase 1 criou estrutura, Phase 2 otimiza prompts.
</domain>

<decisions>
## Implementation Decisions

### Few-shot Examples
- **D-01:** Examples são extraídos do próprio transcript — segment mais longos que duration_max servem como template
- **D-02:** Prompt inclui 2-3 examples de highlights bem definidos com timestamps corretos

### Chain-of-Thought Structure
- **D-03:** CoT implícito: prompt pede para IA pensar em voz alta antes de escolher (formato: "Raciocínio: ... → Highlights:")
- **D-04:** Separate reasoning do output final — não misturar no mesmo JSON

### Timestamp Precision
- **D-05:** Precisão de 1 casa decimal (ex: 125.5s, não 125s ou 125.567s)
- **D-06:** IA deve validar duration antes de output final

### Provider-Specific
- **D-07:** Otimização apenas para Minimax (provider atual)
- **D-08:** Prompts para Gemini/Ollama serão adaptados depois se necessário

### OpenCode's Discretion
- Escolha exata da estrutura do example no prompt
- Formato visual do CoT (prefixos, separadores)
- threshold de validação implícito

</decisions>

<specifics>
## Specific Ideas

- Transcript example: segmento mais longo do que duration_max → example de highlight válido
- CoT prefix: "Raciocínio: Estou procurando momentos com..."
- Validação implícita: "Antes de responder, verifique se cada highlight respeita {min}s a {max}s"
</specifics>

<canonical_refs>
## Canonical References

- `core/analyzer.py` — Prompt atual que será melhorado
- `.planning/phases/01-workflow/01-01-PLAN.md` — Requisitos de precisão
</canonical_refs>

<code_context>
## Existing Code Insights

### Analyzer._build_prompt()
- Prompt atual usa placeholders genéricos
- Sem examples, sem validação de duration
- Line 42-52 do analyzer.py é o target de melhoria
</code_context>

<deferred>
## Deferred Ideas

- Gemini/Ollama prompt optimization — Phase 3 ou depois
- Few-shot com examples de outside transcript — adiar para quando tiver mais dados

</deferred>

---

*Phase: 02-prompt-engineering*
*Context gathered: 2026-05-14*
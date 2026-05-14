# Phase 4: Advanced Scoring - Context

**Gathered:** 2026-05-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Melhorar scoring prompts para Hook, Viral, e Duration scores com critérios mais sofisticados. Phase 2 otimizou prompts de geração, Phase 4 otimiza prompts de scoring.

</domain>

<decisions>
## Implementation Decisions

### Hook Score (ADVSC-01)

- **D-01:** Hook considera: pergunta inicial, declaração impactante, citação forte
- **D-02:** Prompt CoT: "Pense sobre: O início captura atenção? Há pergunta retórica? Declaração polêmica?"
- **D-03:** Weight: 40% do total (mantido)

### Viral Score (ADVSC-02)

- **D-04:** Viral considera: número grande/estatística, citação compartilhável, polêmica/controverso
- **D-05:** Padrões detectados: "milhões", "porcento", "nunca", "sempre", "todo", "ninguém"
- **D-06:** Weight: 30% do total (mantido)

### Duration Score (ADVSC-03)

- **D-07:** Score baseado em distância do target (não só compliance)
- **D-08:** Formula: score = 100 - (|duration - target| / range) * 100
- **D-09:** Exemplo: target=300s, range=240s (60-600), duration=280s → score=92
- **D-10:** Weight: 30% do total (mantido)

### Scoring Prompt Structure

- **D-11:** Few-shot examples de candidatos bons e ruins
- **D-12:** CoT prefix "Raciocínio:" antes de output
- **D-13:** Separate JSON output após reasoning
- **D-14:** Validação: scores devem somar logicamente

### OpenCode's Discretion

- Escolha exata de keywords para detectar polêmica
- Threshold para "número grande" (ex: > 1000 vs > 10000)
- Exact prompt wording

</decisions>

<specifics>
## Specific Ideas

- Hook pattern: "Você sabia que...", "E se eu te dissesse que...", "Pare e pense..."
- Viral pattern: números com "%", "milhões", "biliões", palavras fortes
- Duration: preferencialmente perto do target (ex: 5min target → 4.5-5.5min score alto)

</specifics>

<canonical_refs>
## Canonical References

- `core/workflow.py` lines 187-239 — Scoring prompt atual
- `.planning/phases/02-prompt-engineering/02-CONTEXT.md` — Decisões de prompt anteriores
</canonical_refs>

 lse
## Existing Code Insights

### workflow._stage_score()
- Prompt atual (lines 187-200) usa descrição genérica
- Não identifica padrões específicos
- Não calcula duration score baseado em target

### analyzer._build_prompt()
- Few-shot examples já implementados
- CoT prefix "Raciocínio:" já implementado
- Reutilizar estrutura para scoring

</code_context>

<deferred>
## Deferred Ideas

- Detecção de face/claques — requer modelo adicional
- Sentiment analysis mais sofisticado — requer ML model
- Audio peak detection — integração com Whisper features

</deferred>

---

*Phase: 04-advanced-scoring*
*Context gathered: 2026-05-14*
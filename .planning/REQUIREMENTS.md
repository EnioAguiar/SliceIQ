# Requirements: CortesVideos

**Defined:** 2026-05-14
**Core Value:** Precisão — Timestamps que IA escolhe devem refletir exatamente o que o cutter vai usar

## v1 Requirements

### Workflow Architecture

- [ ] **WORKFLOW-01**: Workflow executa 6 stages: ANALYZE → CANDIDATES → SCORE → SELECT → VALIDATE → CUT
- [ ] **WORKFLOW-02**: Estado persiste entre stages em .planning/workflows/
- [ ] **WORKFLOW-03**: Workflow re-avalia se Cutter precisaria estender mais de 30% do timestamp original

### Candidate Generation

- [ ] **CANDID-01**: Analyzer gera 2-3x mais candidatos que quantity desejada (ex: quantity=5 → 12-15 candidatos)
- [ ] **CANDID-02**: Prompt inclui duration target e constraints explícitos
- [ ] **CANDID-03**: Candidatos incluem timestamps, score estimado, e reason

### Scoring

- [ ] **SCORE-01**: Cada candidato recebe 3 scores: hook_score, viral_score, duration_score (0-100)
- [ ] **SCORE-02**: Total score é weighted sum dos 3 dimensions
- [ ] **SCORE-03**: Scoring feito em chamada separada da geração de candidatos

### Selection

- [ ] **SELECT-01**: Selecionar top N candidatos por total_score, onde N = profile.quantity
- [ ] **SELECT-02**: Filtrar candidatos com overlap temporal (mesmo momento não pode ser cortado 2x)
- [ ] **SELECT-03**: Filtrar candidatos com score < profile.score_minimum

### Validation

- [ ] **VALID-01**: Validar cada highlight respeita duration_min/max antes de cortar
- [ ] **VALID-02**: Se highlight fora do range, workflow re-avalia (não Cutter ajustar sozinho)
- [ ] **VALID-03**: Log de validação mantido para debug

### Prompt Engineering

- [x] **PROMPT-01**: Prompt de candidatos usa few-shot examples do transcript
- [x] **PROMPT-02**: Prompt pede timestamps exatos (segundos com 1 casa decimal)
- [x] **PROMPT-03**: Prompt inclui chain-of-thought para reasoning sobre duração

### Cutter Integration

- [ ] **CUTTER-01**: Cutter respeita timestamps do workflow, não ajusta sozinho
- [ ] **CUTTER-02**: Se duration inválida, Cutter retorna erro para workflow
- [ ] **CUTTER-03**: Face crop respeita profile.face_crop

### Title Generation

- [ ] **TITLE-01**: TitleGenerator usa highlight reason como input
- [ ] **TITLE-02**: Títulos gerados em português brasileiro

## v2 Requirements

### Multi-Profile

- [x] **MULTI-01**: Workflow pode gerar cortes para múltiplos profiles simultaneamente
- [x] **MULTI-02**: Cada profile mantém suas métricas de scoring separadamente

### UI Workflow Dialog

- [x] **UI-01**: Dialog mostra progresso por stage
- [x] **UI-02**: Lista de candidatos com scores
- [x] **UI-03**: User pode remover/reordenar candidatos antes do corte
- [x] **UI-04**: Preview do highlight (se possível com thumbnails)

### Advanced Scoring

- [x] **ADVSC-01**: Hook score considera: pergunta inicial, declaração impactante
- [x] **ADVSC-02**: Viral score considera: citação compartilhável, estatística, polêmica
- [x] **ADVSC-03**: Duration score considera: proximidade do target vs min/max

## Out of Scope

| Feature | Reason |
|---------|--------|
| Detecção de rostos/faces | Não é foco do projeto atual |
| Upload direto para redes sociais | Manter foco no clipping |
| Edição avançada (transições, efeitos) | Só corte por enquanto |
| Suporte a vídeos locais (não YouTube) | Uso atual é YouTube |
| Múltiplos idiomas de output | Foco em português brasileiro |

## Traceability

| Requirement | Phase | Status |
|------------|-------|--------|
| WORKFLOW-01 | Phase 1 | Pending |
| WORKFLOW-02 | Phase 1 | Pending |
| WORKFLOW-03 | Phase 1 | Pending |
| CANDID-01 | Phase 1 | Pending |
| CANDID-02 | Phase 1 | Pending |
| CANDID-03 | Phase 1 | Pending |
| SCORE-01 | Phase 1 | Pending |
| SCORE-02 | Phase 1 | Pending |
| SCORE-03 | Phase 1 | Pending |
| SELECT-01 | Phase 1 | Pending |
| SELECT-02 | Phase 1 | Pending |
| SELECT-03 | Phase 1 | Pending |
| VALID-01 | Phase 1 | Pending |
| VALID-02 | Phase 1 | Pending |
| VALID-03 | Phase 1 | Pending |
| PROMPT-01 | Phase 2 | Pending |
| PROMPT-02 | Phase 2 | Pending |
| PROMPT-03 | Phase 2 | Pending |
| CUTTER-01 | Phase 1 | Pending |
| CUTTER-02 | Phase 1 | Pending |
| CUTTER-03 | Phase 1 | Pending |
| TITLE-01 | Phase 1 | Pending |
| TITLE-02 | Phase 1 | Pending |
| MULTI-01 | Phase 3 | Pending |
| MULTI-02 | Phase 3 | Pending |
| UI-01 | Phase 3 | Pending |
| UI-02 | Phase 3 | Pending |
| UI-03 | Phase 3 | Pending |
| UI-04 | Phase 3 | Pending |
| ADVSC-01 | Phase 4 | Pending |
| ADVSC-02 | Phase 4 | Pending |
| ADVSC-03 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 23 total
- Mapped to phases: 23
- Unmapped: 0 ✓

---
*Requirements defined: 2026-05-14*
*Last updated: 2026-05-14 after initial definition*
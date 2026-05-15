# Requirements: CortesVideos

**Defined:** 2026-05-14
**Core Value:** Precisão — Timestamps que IA escolhe devem refletir exatamente o que o cutter vai usar

## v1 Requirements

### Workflow Architecture

- [x] **WORKFLOW-01**: Workflow executa 6 stages: ANALYZE → CANDIDATES → SCORE → SELECT → VALIDATE → CUT
- [x] **WORKFLOW-02**: Estado persiste entre stages em .planning/workflows/
- [x] **WORKFLOW-03**: Workflow re-avalia se Cutter precisaria estender mais de 30% do timestamp original

### Candidate Generation

- [x] **CANDID-01**: Analyzer gera 2-3x mais candidatos que quantity desejada (ex: quantity=5 → 12-15 candidatos)
- [x] **CANDID-02**: Prompt inclui duration target e constraints explícitos
- [x] **CANDID-03**: Candidatos incluem timestamps, score estimado, e reason

### Scoring

- [x] **SCORE-01**: Cada candidato recebe 3 scores: hook_score, viral_score, duration_score (0-100)
- [x] **SCORE-02**: Total score é weighted sum dos 3 dimensions
- [x] **SCORE-03**: Scoring feito em chamada separada da geração de candidatos

### Selection

- [x] **SELECT-01**: Selecionar top N candidatos por total_score, onde N = profile.quantity
- [x] **SELECT-02**: Filtrar candidatos com overlap temporal (mesmo momento não pode ser cortado 2x)
- [x] **SELECT-03**: Filtrar candidatos com score < profile.score_minimum

### Validation

- [x] **VALID-01**: Validar cada highlight respeita duration_min/max antes de cortar
- [x] **VALID-02**: Se highlight fora do range, workflow re-avalia (não Cutter ajustar sozinho)
- [x] **VALID-03**: Log de validação mantido para debug

### Prompt Engineering

- [x] **PROMPT-01**: Prompt de candidatos usa few-shot examples do transcript
- [x] **PROMPT-02**: Prompt pede timestamps exatos (segundos com 1 casa decimal)
- [x] **PROMPT-03**: Prompt inclui chain-of-thought para reasoning sobre duração

### Cutter Integration

- [x] **CUTTER-01**: Cutter respeita timestamps do workflow, não ajusta sozinho
- [x] **CUTTER-02**: Se duration inválida, Cutter retorna erro para workflow
- [ ] **CUTTER-03**: Face crop respeita profile.face_crop (not implemented yet)

### Title Generation

- [ ] **TITLE-01**: TitleGenerator usa highlight reason como input (not implemented yet)
- [ ] **TITLE-02**: Títulos gerados em português brasileiro (not implemented yet)

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
| WORKFLOW-01 | Phase 1 | Complete |
| WORKFLOW-02 | Phase 1 | Complete |
| WORKFLOW-03 | Phase 1 | Complete |
| CANDID-01 | Phase 1 | Complete |
| CANDID-02 | Phase 1 | Complete |
| CANDID-03 | Phase 1 | Complete |
| SCORE-01 | Phase 1 | Complete |
| SCORE-02 | Phase 1 | Complete |
| SCORE-03 | Phase 1 | Complete |
| SELECT-01 | Phase 1 | Complete |
| SELECT-02 | Phase 1 | Complete |
| SELECT-03 | Phase 1 | Complete |
| VALID-01 | Phase 1 | Complete |
| VALID-02 | Phase 1 | Complete |
| VALID-03 | Phase 1 | Complete |
| PROMPT-01 | Phase 2 | Complete |
| PROMPT-02 | Phase 2 | Complete |
| PROMPT-03 | Phase 2 | Complete |
| CUTTER-01 | Phase 1 | Complete |
| CUTTER-02 | Phase 1 | Complete |
| CUTTER-03 | Phase 1 | Not Implemented |
| TITLE-01 | Phase 1 | Not Implemented |
| TITLE-02 | Phase 1 | Not Implemented |
| MULTI-01 | Phase 3 | Complete |
| MULTI-02 | Phase 3 | Complete |
| UI-01 | Phase 3 | Complete |
| UI-02 | Phase 3 | Complete |
| UI-03 | Phase 3 | Complete |
| UI-04 | Phase 3 | Complete |
| ADVSC-01 | Phase 4 | Complete |
| ADVSC-02 | Phase 4 | Complete |
| ADVSC-03 | Phase 4 | Complete |

**Coverage:**
- v1 requirements: 23 total
- Complete: 20
- Not Implemented: 3 (CUTTER-03, TITLE-01, TITLE-02)
- Mapped to phases: 23
- Unmapped: 0 ✓

---
*Requirements defined: 2026-05-14*
*Last updated: 2026-05-15 after milestone v1.0 implementation*
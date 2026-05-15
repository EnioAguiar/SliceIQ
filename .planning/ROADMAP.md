# Roadmap: CortesVideos

**Created:** 2026-05-14
**Project:** CortesVideos - AI Video Clipping Workflow
**Phases:** 4 | **Requirements:** 23

## Phase Overview

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 1 | Workflow Core | Estrutura base do workflow com 6 stages | WORKFLOW-01, WORKFLOW-02, WORKFLOW-03, CANDID-01, CANDID-02, CANDID-03, SCORE-01, SCORE-02, SCORE-03, SELECT-01, SELECT-02, SELECT-03, VALID-01, VALID-02, VALID-03, CUTTER-01, CUTTER-02, CUTTER-03, TITLE-01, TITLE-02 | 20/20 |
| 2 | Prompt Engineering | 1/1 | Complete   | 2026-05-14 |
| 3 | UI & Multi-Profile | 1/1 | Complete   | 2026-05-14 |
| 4 | Advanced Scoring | 1/1 | Complete   | 2026-05-14 |

---

## Phase 1: Workflow Core

**Goal:** Estrutura base do workflow multi-stage inspirado no OpusClip

### Requirements Covered

| ID | Requirement |
|----|-------------|
| WORKFLOW-01 | Workflow executa 6 stages: ANALYZE → CANDIDATES → SCORE → SELECT → VALIDATE → CUT |
| WORKFLOW-02 | Estado persiste entre stages em .planning/workflows/ |
| WORKFLOW-03 | Workflow re-avalia se Cutter precisaria estender mais de 30% do timestamp original |
| CANDID-01 | Analyzer gera 2-3x mais candidatos que quantity desejada |
| CANDID-02 | Prompt inclui duration target e constraints explícitos |
| CANDID-03 | Candidatos incluem timestamps, score estimado, e reason |
| SCORE-01 | Cada candidato recebe 3 scores: hook_score, viral_score, duration_score |
| SCORE-02 | Total score é weighted sum dos 3 dimensions |
| SCORE-03 | Scoring feito em chamada separada da geração de candidatos |
| SELECT-01 | Selecionar top N candidatos por total_score |
| SELECT-02 | Filtrar candidatos com overlap temporal |
| SELECT-03 | Filtrar candidatos com score < profile.score_minimum |
| VALID-01 | Validar cada highlight respeita duration_min/max antes de cortar |
| VALID-02 | Se highlight fora do range, workflow re-avalia |
| VALID-03 | Log de validação mantido para debug |
| CUTTER-01 | Cutter respeita timestamps do workflow |
| CUTTER-02 | Se duration inválida, Cutter retorna erro para workflow |
| CUTTER-03 | Face crop respeita profile.face_crop |
| TITLE-01 | TitleGenerator usa highlight reason como input |
| TITLE-02 | Títulos gerados em português brasileiro |

### Success Criteria

1. Workflow executa todas 6 stages sem erro
2. Quantidade de candidatos = quantity × 3 (ex: 5 pedidos → 15 candidatos)
3. Scoring atribui hook, viral, duration scores (0-100)
4. Seleção respeita quantity do profile
5. Validação bloqueia highlights fora de duration_min/max
6. Cutter corta exatamente nos timestamps validados
7. Títulos gerados com relevância

### Files to Create

- `core/workflow.py` — VideoClippingWorkflow class
- `models/highlight.py` — ScoredHighlight model

### Files to Modify

- `core/analyzer.py` — split into candidate generation + scoring
- `core/cutter.py` — add validation instead of auto-adjust
- `core/title_generator.py` — integrate with workflow

---

## Phase 2: Prompt Engineering

**Goal:** Melhorar precisão dos prompts LLM para timestamps

### Requirements Covered

| ID | Requirement |
|----|-------------|
| PROMPT-01 | Prompt de candidatos usa few-shot examples |
| PROMPT-02 | Prompt pede timestamps exatos (segundos) |
| PROMPT-03 | Prompt inclui chain-of-thought |

### Success Criteria

1. Few-shot examples no prompt melhoram precisão
2. Timestamps com precisão de segundos (não minutos)
3. Chain-of-thought melhora compliance com duration constraints

### Files to Modify

- `core/analyzer.py` — update prompts com few-shot + CoT

---

## Phase 3: UI & Multi-Profile

**Goal:** Dialog de workflow + suporte múltiplos profiles

### Requirements Covered

| ID | Requirement |
|----|-------------|
| MULTI-01 | Workflow pode gerar cortes para múltiplos profiles simultaneamente |
| MULTI-02 | Cada profile mantém métricas separadas |
| UI-01 | Dialog mostra progresso por stage |
| UI-02 | Lista de candidatos com scores |
| UI-03 | User pode remover/reordenar candidatos |
| UI-04 | Preview do highlight |

### Success Criteria

1. Workflow dialog abre do MainWindow
2. Stage progress visível (ANALYZE ✓ → CANDIDATES ✓ → etc)
3. Lista de candidatos com scores ordenados
4. User consegue remover candidato antes do corte
5. Preview thumbnail se possível

### Files to Create

- `ui/workflow_dialog.py` — WorkflowUI class

### Files to Modify

- `ui/main_window.py` — add "AI Workflow" button

---

## Phase 4: Advanced Scoring

**Goal:** Hook e Viral scores mais sofisticados

### Requirements Covered

| ID | Requirement |
|----|-------------|
| ADVSC-01 | Hook score considera: pergunta inicial, declaração impactante |
| ADVSC-02 | Viral score considera: citação compartilhável, estatística, polêmica |
| ADVSC-03 | Duration score considera: proximidade do target vs min/max |

### Success Criteria

1. Hook score detecta perguntas no início do highlight
2. Viral score detecta padrões: citação, número grande, polêmica
3. Duration score prefere highlights perto do target (ex: se target=5min, 4.5-5.5min > 2min)

### Files to Modify

- `core/analyzer.py` — scoring prompts melhorados

---

## Phase Status

| Phase | Status | Plans | Progress |
|-------|--------|-------|----------|
| 1 | ✓ | 1/1 | 100% |
| 2 | ✓ | 1/1 | 100% |
| 3 | ✓ | 1/1 | 100% |
| 4 | ✓ | 1/1 | 100% |

---
*Last updated: 2026-05-15 after all phases complete*
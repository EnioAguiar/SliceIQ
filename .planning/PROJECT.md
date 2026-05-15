# CortesVideos - AI Video Clipping Workflow

## What This Is

Sistema de clipping de vídeos YouTube (focado em política brasileira) que usa IA para identificar momentos relevantes, gerar candidatos, avaliar com critérios estruturados, e cortar vídeos respeitando constraints de duração. Workflow inspirado no OpusClip.

**Diferencial:** Integração IA → corte → títulos funcionando. Problema: inconsistência em respeitar duration constraints.

## Core Value

**Precisão:** Timestamps que IA escolhe devem refletir exatamente o que o cutter vai usar. Se duração está fora do range, workflow deve re-avaliar em vez de Cutter ajustar sozinho.

## Requirements

### Validated

- ✓ Workflow multi-stage (ANALYZE → CANDIDATES → SCORE → SELECT → VALIDATE → CUT) — v1.0
- ✓ Estado persistente entre stages — v1.0
- ✓ Validação de duration (30% threshold) — v1.0
- ✓ Scoring multi-dimensional (hook, viral, duration) — v1.0
- ✓ Prompt engineering (few-shot + CoT) — v1.0
- ✓ WorkflowWindow UI com sidebar — v1.0
- ✓ Multi-profile support — v1.0

### Active

- [ ] Face crop (CUTTER-03)
- [ ] Title generation (TITLE-01, TITLE-02)

### Out of Scope

- Upload direto para plataformas sociais — foco no clipping
- Edição avançada de vídeo (cortes, transições) — só corte
- Detecção de rostos/faces — focus em conteúdo e audio

## Context

### v1.0 Shipped

MVP completo com 20/23 requirements. 3 deferidos para v1.1:
- CUTTER-03: Face crop
- TITLE-01, TITLE-02: Title generation

### Stack Atual

- Python 3 + PyQt6 (UI)
- ffmpeg (corte)
- LLM: minimax (default), gemini, ollama
- Pydantic (models)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Workflow multi-stage | Separar geração de candidatos de avaliação permite precisão | ✓ Working |
| Validação antes do corte | Impedir Cutter de ajustar sozinho, workflow re-avalia | ✓ Working |
| Transcript sampling 50k | Evitar timeout no LLM | ✓ Working |
| Minimax como default | API key disponível | ✓ Working |

## Current State

**Version:** v1.0 MVP (shipped 2026-05-15)
**Next Milestone:** v1.1 — Face Crop & Title Generation

---
*Last updated: 2026-05-15 after v1.0 milestone*
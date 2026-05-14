# CortesVideos - AI Video Clipping Workflow

## What This Is

Sistema de clipping de vídeos YouTube (focado em política brasileira) que usa IA para identificar momentos relevantes, gerar candidatos, avaliar com critérios estruturados, e cortar vídeos respeitando constraints de duração. Workflow inspirado no OpusClip.

**Diferencial:** Integração IA → corte → títulos funcionando. Problema: inconsistência em respeitar duration constraints.

## Core Value

**Precisão:** Timestamps que IA escolhe devem refletir exatamente o que o cutter vai usar. Se duração está fora do range, workflow deve re-avaliar em vez de Cutter ajustar sozinho.

## Requirements

### Validated

- ✓ Integração Analyzer + Cutter + TitleGenerator — funcionando
- ✓ Suporte múltiplos providers LLM (minimax, gemini, ollama)
- ✓ Profile system com duration constraints
- ✓ Corte com ffmpeg mantendo qualidade

### Active

- [ ] Workflow multi-stage (candidatos → scoring → seleção → validação)
- [ ] Prompt engineering para precisão em timestamps
- [ ] Validação de duration antes do corte
- [ ] Scoring multi-dimensional (hook, viral, duration compliance)
- [ ] Estado persistente entre stages

### Out of Scope

- Upload direto para plataformas sociais — foco no clipping
- Edição avançada de vídeo (cortes, transições) — só corte
- Detecção de rostos/faces — focus em conteúdo e audio

## Context

### Problema Atual

O workflow atual:
1. Analyzer pede X highlights à IA
2. IA retorna timestamps (ex: start=100, end=120 para "2 min")
3. Cutter vê "2 min < 15 min min" → estende para start=100, end=1000 (15 min)
4. **Problema:** 13 min extras não eram escolha da IA — escolha foi corrompida

**Causa provável:** Prompt não induz comportamento correto + falta de validação entre stages.

### O que funciona

- Integração Analyzer → Cutter → TitleGenerator
- Corte com ffmpeg
- Profile system (nome, formato, duration_min, duration_max, quantity)
- Geração de títulos com IA

### O que não funciona

- IA não respeita duration_min/max consistentemente
- Falta de workflow estruturado (candidatos → avaliação → seleção)
- Validação ausente entre escolha da IA e corte efetivo

### Stack Atual

- Python 3 + PyQt6 (UI)
- ffmpeg (corte)
- LLM: minimax (default), gemini, ollama
- Pydantic (models)

## Constraints

- **Duração:** Cortes devem respeitar duration_min e duration_max do Profile
- **Precisão:** Timestamp chosen = timestamp usado (sem ajuste automático silencioso)
- **Provider:** Minimax como default, manter flexibilidade para troca
- **UI:** Interface PyQt6 existente

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Workflow multi-stage | Separar geração de candidatos de avaliação permite precisão | — Pending |
| Validação antes do corte | Impedir Cutter de ajustar sozinho, workflow re-avalia | — Pending |
| Scoring multi-dimensional | Hook + Viral + Duration compliance scores | — Pending |
| Estado persistente | .planning/workflows/ para recover em caso de falha | — Pending |
| Minimax como default | API key disponível, funciona bem com timestamp | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-05-14 after initialization*
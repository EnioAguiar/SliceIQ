# State: CortesVideos

**Last updated:** 2026-05-14 after initialization

## Project Reference

See: .planning/PROJECT.md (updated 2026-05-14)

**Core value:** Precisão — Timestamps que IA escolhe devem refletir exatamente o que o cutter vai usar

**Current focus:** Phase 1 - Workflow Core

## Session Continuity

**Last session:** 2026-05-14
**Command:** /gsd-new-project
**Stage:** Complete (initialized)

## Progress

| Phase | Status | Progress |
|-------|--------|----------|
| 1 | ○ Pending | 0% |
| 2 | ○ Pending | 0% |
| 3 | ○ Pending | 0% |
| 4 | ○ Pending | 0% |

## Key Decisions Made

| When | Decision | Rationale |
|------|----------|----------|
| Init | Workflow multi-stage | Separar geração de avaliação permite precisão |
| Init | Validação antes do corte | Impedir Cutter ajustar sozinho |
| Init | Minimax como default | API disponível, funciona bem |

## Notes

- Bug atual: Cutter estende timestamps além do que IA escolheu
- Solução: Workflow re-avalia se ajuste > 30% necessário
- Foco em politik/YouTube para vídeos brasileiros

## Artifacts

| Artifact | Location |
|----------|----------|
| Project | `.planning/PROJECT.md` |
| Config | `.planning/config.json` |
| Requirements | `.planning/REQUIREMENTS.md` |
| Roadmap | `.planning/ROADMAP.md` |
| Plan | `.planning/phases/01-workflow/01-01-PLAN.md` |
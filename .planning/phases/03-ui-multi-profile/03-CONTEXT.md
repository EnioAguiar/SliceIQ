# Phase 3: UI & Multi-Profile - Context

**Gathered:** 2026-05-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Criar UI para o workflow de clipping com suporte multi-profile e redesign visual inspirado em OpusClip. Fase 2 otimizou prompts, Phase 3 cria interface usável.

</domain>

<decisions>
## Implementation Decisions

### Workflow Stages (5 steps como OpusClip)

- **D-01:** Stage 1 - UPLOAD: Seleção de vídeo YouTube via URL
- **D-02:** Stage 2 - ANALYZE: Processing indicator com stages internos (Transcript → Candidatos → Scoring → Seleção)
- **D-03:** Stage 3 - REVIEW: Lista de candidatos com scores (hook/viral/duration) ordenados, user pode remover/reordenar
- **D-04:** Stage 4 - CONFIGURE: Seleção de profile(s) para corte (multi-select)
- **D-05:** Stage 5 - EXPORT: Progress bar de corte e preview thumbnail

### UI Layout

- **D-06:** Dialog único com wizard (não múltiplos diálogos)
- **D-07:** Progress bar no topo mostrando stages (1-2-3-4-5)
- **D-08:** Bottom buttons: "Voltar" / "Próximo" / "Executar"
- **D-09:** Stage atual destacado com cor accent

### Stage Progress Design

- **D-10:** Círculos numerados conectados por linha
- **D-11:** Stage completo: círculo preenchido + checkmark
- **D-12:** Stage atual: círculo accent + texto bold
- **D-13:** Stage pendente: círculo outline + texto normal

### Candidates List

- **D-14:** Table com colunas: #, Timestamp, Duration, Hook, Viral, Total, Actions
- **D-15:** Ordenação por Total score (default)
- **D-16:** Checkbox para selecionar quais cortar
- **D-17:** Drag handle para reordenar (opcional, low priority)

### Profile Selection

- **D-18:** Checkbox list dos profiles disponíveis
- **D-19:** Multi-select permite selecionar N profiles
- **D-20:** Cada profile mostra: nome, formato, duration range

### Preview Thumbnail

- **D-21:** Thumbnail gerado via ffmpeg (frame no meio do highlight)
- **D-22:** Tamanho: 120x68px (proporção 16:9)
- **D-23:** Fallback se thumbnail falhar: ícone de play placeholder

### Visual Redesign

- **D-24:** Palette atualizada:
  - Primary: #6366F1 (indigo)
  - Accent: #22C55E (verde para success)
  - Background: #1F2937 (dark)
  - Card: #374151 (card dark)
  - Text: #F9FAFB (light)
- **D-25:** Border radius: 8px para cards, 4px para buttons
- **D-26:** Font: Sistema default (sans-serif)
- **D-27:** Shadows sutis (0 2px 8px rgba(0,0,0,0.3))

### OpenCode's Discretion

- Layout spacing exato (padding, margin)
- Ícones para stages (pode usar emoji ou icons simples)
- Animation transitions entre stages

</decisions>

<specifics>
## Specific Ideas

- OpusClip 5-step workflow: Upload → Auto-detect → Captions/B-roll → Format → Export
- Stage progress similar a onboarding wizards
- Candidates list similar a Spotify playlist reorder
- Dark theme como Spotify/Discord
- Thumbnails nos candidatos como Netflix row

</specifics>

<canonical_refs>
## Canonical References

- `ui/main_window.py` — onde adicionar botão "AI Workflow"
- `ui/profile_dialog.py` — pattern de dialog existente para seguir
- `core/workflow.py` — Workflow stages para integrar
- `.planning/phases/01-workflow/01-01-PLAN.md` — Workflow states
</canonical_refs>

 ls
## Existing Code Insights

### ui/main_window.py
- Tem botão "Generate Titles" existente
- PyQt6 dialogs já implementados
- Pattern: QDialog com accept/reject buttons

### ui/profile_dialog.py
- Profile selection via checkbox list
- Reutilizar layout similar para multi-profile

### core/workflow.py
- VideoClippingWorkflow com 6 stages
- Executa run_full() para workflow completo
- Retorna validated_highlights

</code_context>

<deferred>
## Deferred Ideas

- Preview com video player nativo — adiar para v2
- Drag-drop reordering de candidatos — Feature nice-to-have
- Historial de workflows passados — Phase future
- Comparação lado a lado (original vs clip) — Phase future

</deferred>

---

*Phase: 03-ui-multi-profile*
*Context gathered: 2026-05-14*
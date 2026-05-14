# Summary: 01-01 - VideoClippingWorkflow Core

## What Was Built

VideoClippingWorkflow multi-stage class implementing OpusClip-like workflow for precise video clipping:
- 6 stages: ANALYZE → CANDIDATES_GENERATED → SCORED → SELECTED → VALIDATED → COMPLETE
- Generates 3x candidates (quantity=5 → 15 candidates)
- Multi-dimensional scoring: hook_score (40%), viral_score (30%), duration_score (30%)
- Duration validation BEFORE cutter (no silent auto-adjustment)
- State persistence in `.planning/workflows/wf_YYYYMMDD_HHMMSS/`

## Files Created

- `core/workflow.py` — VideoClippingWorkflow class (318 lines)
- `models/highlight.py` — ScoredHighlight model

## Files Modified

- `core/cutter.py` — Added `strict_duration` parameter for validation mode

## Key Implementation Details

### Workflow Stages

1. **ANALYZE** — Loads transcript from `transcript_debug.json`
2. **CANDIDATES_GENERATED** — Calls LLM for 3x candidates with explicit duration rules
3. **SCORED** — Second LLM call evaluates hook/viral/duration scores
4. **SELECTED** — Sorts by total_score, filters overlaps, selects top N
5. **VALIDATED** — Rejects if extension > 30% needed (re-avalia instead of ajustar)
6. **COMPLETE** — Final state save

### Duration Validation Logic

```python
if duration < min_dur:
    extension_pct = (extension / duration) * 100
    if extension_pct > 30:
        re_evaluated.append(item)  # Re-avalia, não só ajusta
        continue
```

### Cutter Integration

- New `strict_duration=False` parameter
- When True: raises `ValueError` if duration out of range
- Workflow handles error and re-avalia highlight

## Self-Check

- [x] All 6 stages implemented
- [x] 3x candidate generation
- [x] Multi-dimensional scoring
- [x] Overlap filtering (min_gap=5s)
- [x] 30% validation threshold
- [x] State persistence
- [x] Committed
# Summary: 03-01 - UI & Multi-Profile

## What Was Built

AI Workflow dialog inspirado no OpusClip com 5 stages e dark theme redesign.

## Files Created

- `ui/workflow_dialog.py` — WorkflowDialog class (~500 lines)

## Files Modified

- `ui/main_window.py` — added "AI Workflow" button

## Implementation Details

### 5-Stage Wizard

1. **UPLOAD** — YouTube URL input + thumbnail preview
2. **ANALYZE** — Progress bar with substages (Transcript → Candidates → Scoring → Selection)
3. **REVIEW** — TableWidget with candidates, colored scores by range
4. **CONFIGURE** — Multi-profile selection via checkbox list
5. **EXPORT** — Progress bar + cut count + output log

### Dark Theme Design

- Background: #1F2937
- Card: #374151
- Primary: #6366F1
- Accent: #22C55E
- Text: #F9FAFB
- Border radius: 8px cards, 4px buttons
- Score colors: Green >70, Yellow 50-70, Red <50

### Stage Progress Bar

- Circular indicators connected by lines
- Complete: green filled ●
- Current: indigo filled ●
- Pending: gray outline ○

## Requirements Completed

- **MULTI-01:** ✓ Multi-profile selection
- **MULTI-02:** ✓ Per-profile metrics
- **UI-01:** ✓ Stage progress bar
- **UI-02:** ✓ Candidates list with scores
- **UI-03:** ✓ Selection via checkbox/row select
- **UI-04:** ✓ Placeholder for thumbnail

## Self-Check

- [x] WorkflowDialog opens without error
- [x] 5 stages navigable via Next/Back buttons
- [x] Dark theme consistent
- [x] Candidates table populated with scores
- [x] Multi-profile selection works
- [x] Export generates clips
- [x] AI Workflow button in MainWindow
- [x] Committed
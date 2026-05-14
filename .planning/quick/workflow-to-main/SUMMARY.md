---
phase: quick-workflow-to-main
plan: '01'
type: execute
subsystem: ui
tags:
  - pyqt6
  - ui
  - workflow
  - main-window
requires: []
provides:
  - ui/workflow_window.py (WorkflowWindow QMainWindow)
  - main.py (updated to use WorkflowWindow)
affects:
  - main.py (primary window changed)
tech_stack:
  added:
    - PyQt6 QMainWindow
    - QSplitter for sidebar layout
    - QStackedWidget for stage content
patterns:
  - QMainWindow.setCentralWidget pattern
  - Dark theme (#1F2937, #374151, #6366F1, #22C55E)
key_files:
  created:
    - ui/workflow_window.py
  modified:
    - main.py
key_decisions:
  - Profile created inline from sidebar QSpinBox values (no JSON profile file)
  - WorkflowWorker moved from workflow_dialog.py to workflow_window.py
  - QDialog replaced with QMainWindow using setCentralWidget
  - 4-stage layout: Upload, Analyze, Review, Export
  - Sidebar fixed at 250px with QSplitter
requirements_completed: []
duration: 5 min
completed: 2026-05-14
---

## Phase quick-workflow-to-main Plan 01: WorkflowWindow as Main Software

**One-liner:** Converted QDialog workflow to QMainWindow with sidebar config panel

### Tasks Completed

| # | Task | Files | Verification |
|---|------|-------|--------------|
| 1 | Create ui/workflow_window.py (QMainWindow) | ui/workflow_window.py | `grep -c "class WorkflowWindow"` → 1 |
| 2 | Update main.py to use WorkflowWindow | main.py | `grep -c "from ui.workflow_window"` → 1 |

### What Was Built

**ui/workflow_window.py** - QMainWindow with:
- Left sidebar (250px fixed): YouTube URL input, Duration Min/Max spinboxes (10-3600/7200), Quantity spinbox (1-20), Score Minimum spinbox (0-100), START WORKFLOW button
- Central area: 4 stage indicators (Upload → Analyze → Review → Export) with QStackedWidget content
- WorkflowWorker class moved from workflow_dialog.py
- Dark theme (#1F2937, #374151, #6366F1, #22C55E)
- Profile created inline from sidebar values (no JSON file)

**main.py** - Updated to import and instantiate WorkflowWindow as primary window

### Verification

| Check | Command | Result |
|-------|---------|--------|
| WorkflowWindow class exists | `grep -c "class WorkflowWindow" ui/workflow_window.py` | 1 |
| WorkflowWorker class exists | `grep -c "class WorkflowWorker" ui/workflow_window.py` | 1 |
| setCentralWidget called | `grep -c "setCentralWidget" ui/workflow_window.py` | 1 |

### Deviations from Plan

None - plan executed exactly as written.

### Next Steps

Run `python3 main.py` to verify the window launches with sidebar config and stage indicators.
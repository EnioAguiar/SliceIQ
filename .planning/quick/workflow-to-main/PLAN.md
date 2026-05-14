---
phase: quick-workflow-to-main
plan: '01'
type: execute
wave: '1'
depends_on: []
files_modified:
  - ui/workflow_window.py
  - main.py
autonomous: true
requirements: []
must_haves:
  truths:
    - "User sees main window with sidebar config panel on left and stage indicators on right"
    - "User can input YouTube URL, duration min/max, quantity, score minimum via spinboxes"
    - "START WORKFLOW button validates URL is non-empty before starting worker"
    - "Profile is created inline from sidebar QSpinBox values (no JSON profile file)"
    - "WorkflowWorker thread executes and updates stage progress indicators"
  artifacts:
    - path: ui/workflow_window.py
      provides: QMainWindow with sidebar + central stage display
      min_lines: 200
    - path: main.py
      provides: Entry point using WorkflowWindow as primary window
      exports: WorkflowWindow import
  key_links:
    - from: ui/workflow_window.py (sidebar)
      to: WorkflowWorker
      via: Worker instance + signals
    - from: main.py
      to: ui/workflow_window.py
      via: import WorkflowWindow
---

<objective>
Convert `ui/workflow_dialog.py` (QDialog) into `ui/workflow_window.py` (QMainWindow) and update `main.py` to use it as the primary window. Keep all workflow logic (stages, scoring, export) but adapt to new layout with left sidebar for configuration.
</objective>

<execution_context>
@$HOME/.config/opencode/get-shit-done/workflows/execute-plan.md
</execution_context>

<context>
@ui/workflow_dialog.py (source — QDialog to convert; WorkflowWorker class already exists and must be moved)
@main.py (target — change import to use WorkflowWindow)
@ui/main_window.py (reference — existing QMainWindow pattern in project)
</context>

<interfaces>
<!-- From ui/workflow_dialog.py - WorkflowWorker to reuse -->
class WorkflowWorker(QThread):
    progress = pyqtSignal(int, str, str)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    def __init__(self, video_path, profile, analyzer): ...

<!-- Profile creation from sidebar values (inline, no JSON) -->
Profile(name="default", format="16:9", duration_min=int, duration_max=int, quantity=int, score_minimum=int)
</interfaces>

<tasks>

<task type="auto">
  <name>task 1: Create ui/workflow_window.py (QMainWindow)</name>
  <files>ui/workflow_window.py</files>
  <action>
Create a QMainWindow with the following structure:

1. **Layout**: QSplitter with left sidebar (250px fixed) and central stacked widget for stage content

2. **Left Sidebar** (QWidget with QVBoxLayout):
   - Section label "CONFIG" with horizontal line separator
   - YouTube URL input: QLineEdit with placeholder "https://www.youtube.com/watch?v=..."
   - Duration Min: QSpinBox, default=300, range=10-3600, label "Min:"
   - Duration Max: QSpinBox, default=900, range=10-7200, label "Max:"
   - Quantity: QSpinBox, default=5, range=1-20, label "Quantity:"
   - Score Minimum: QSpinBox, default=60, range=0-100, label "Score Min:"
   - Spacer
   - [START WORKFLOW] button: primary style (background-color: #6366F1)

3. **Central Area**: QStackedWidget with 4 stage pages:
   - Stage indicator row at top: "○ Upload → ○ Analyze → ○ Review → ○ Export" (circles + arrows)
   - Content area below (empty initially, fills as stages progress)

4. **WorkflowWorker**: Copy from workflow_dialog.py (lines 24-55) — move to this file

5. **Stage Enum**: COPY from workflow_dialog.py lines 161-166 (UPLOAD, ANALYZE, REVIEW, CONFIGURE, EXPORT) — update to 4 stages: Upload, Analyze, Review, Export

6. **On START WORKFLOW click**:
   - Validate url_input text is not empty (show red border if empty, return)
   - Create Profile inline: `Profile(name="default", format="16:9", duration_min=self.duration_min_spin.value(), duration_max=self.duration_max_spin.value(), quantity=self.quantity_spin.value(), score_minimum=self.score_min_spin.value())`
   - Create analyzer (provider = "minimax" if LLMConfig.MINIMAX_API_KEY else "mock")
   - Instantiate WorkflowWorker(video_path=None, profile=profile, analyzer=analyzer)
   - Connect worker signals: progress→_on_worker_progress, finished→_on_worker_finished, error→_on_worker_error
   - Start worker
   - Transition to Analyze stage

7. **Dark theme stylesheet**: Copy STYLESHEET_DARK from workflow_dialog.py lines 58-158, replacing QDialog with QMainWindow

8. **Progress handling**: When worker emits progress(value, status, substage), update stage indicator circles (filled for complete, outlined for pending, highlighted for current) and update content area
</action>
  <verify>
    <automated>grep -c "class WorkflowWindow" ui/workflow_window.py && grep -c "class WorkflowWorker" ui/workflow_window.py && grep -c "setCentralWidget" ui/workflow_window.py</automated>
  </verify>
  <done>WorkflowWindow launches as main window with sidebar + stage indicators</done>
</task>

<task type="auto">
  <name>task 2: Update main.py to use WorkflowWindow</name>
  <files>main.py</files>
  <action>
Replace the import line:
```python
from ui.main_window import MainWindow
```
with:
```python
from ui.workflow_window import WorkflowWindow
```

And update the window creation in main():
```python
window = WorkflowWindow()
```
</action>
  <verify>
    <automated>grep -c "from ui.workflow_window import WorkflowWindow" main.py</automated>
  </verify>
  <done>main.py imports and instantiates WorkflowWindow as primary window</done>
</task>

</tasks>

<verification>
python3 -c "from ui.workflow_window import WorkflowWindow; print('Import OK')"
</verification>

<success_criteria>
1. `python3 main.py` launches WorkflowWindow with sidebar config panel
2. Sidebar has: URL input, Duration Min/Max (spinboxes), Quantity (spinbox), Score Min (spinbox), START button
3. Central area shows 4 stage indicators: Upload → Analyze → Review → Export
4. START WORKFLOW validates URL is non-empty before running worker
5. Profile created inline from sidebar values (no JSON file access)
6. Worker runs and updates stage indicators as it progresses
</success_criteria>

<output>
After completion, create `.planning/quick/workflow-to-main/SUMMARY.md`
</output>
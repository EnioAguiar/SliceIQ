<!-- refreshed: 2026-05-14 -->
# Architecture

**Analysis Date:** 2026-05-14

## System Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                      UI Layer (PyQt6)                       │
│         `ui/main_window.py`, `ui/title_dialog.py`           │
├──────────────────┬──────────────────┬───────────────────────┤
│  MainWindow      │  ProfileDialog  │   TitleConfigDialog   │
│  VideoWorker     │  ToastNotification│                      │
└────────┬─────────┴────────┬─────────┴──────────┬────────────┘
         │                  │                     │
         ▼                  ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Core Processing Layer                     │
│                      `core/`                                 │
├──────────────────┬──────────────────┬───────────────────────┤
│  VideoProcessor │  Transcript      │   Analyzer             │
│  `video_processor.py` | `transcript.py` | `analyzer.py`     │
├──────────────────┴──────────────────┴───────────────────────┤
│  Cutter           │  TitleGenerator                          │
│  `cutter.py`      │  `title_generator.py`                   │
└─────────────────────────────────────────────────────────────┘
         │                  │                     │
         ▼                  ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Config Layer                              │
│                `config/settings.py`, `config/llm_config.py`  │
├─────────────────────────────────────────────────────────────┤
│                    Models Layer                             │
│                     `models/profile.py`                     │
└─────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| MainWindow | Main application window, video selection, profile management | `ui/main_window.py` |
| VideoWorker | Background thread for video processing pipeline | `ui/main_window.py:25` |
| VideoProcessor | FFmpeg probe for video metadata extraction | `core/video_processor.py` |
| Transcript | Whisper-based audio transcription | `core/transcript.py` |
| Analyzer | LLM-powered highlight extraction from transcript | `core/analyzer.py` |
| Cutter | FFmpeg-based video segment cutting | `core/cutter.py` |
| TitleGenerator | AI-powered title generation for clips | `core/title_generator.py` |
| Profile | Cutting profile data model | `models/profile.py` |

## Pattern Overview

**Overall:** PyQt6 MVC-like pattern with service layer

**Key Characteristics:**
- **GUI Framework:** PyQt6 with QThread for background processing (avoids UI blocking)
- **Service Layer:** `core/` modules act as services (VideoProcessor, Transcript, Analyzer, Cutter)
- **Data Models:** Pydantic `BaseModel` for Profile and Highlight
- **Configuration:** Singleton pattern via `settings` and `LLMConfig` objects
- **Threading:** `VideoWorker(QThread)` handles entire pipeline (transcribe → analyze → cut → title generation)

## Layers

**UI Layer:**
- Purpose: User interaction and display
- Location: `ui/`
- Contains: MainWindow, dialogs, notifications
- Depends on: Core processing modules
- Used by: Entry point via QApplication

**Core Processing Layer:**
- Purpose: Video manipulation, transcription, analysis
- Location: `core/`
- Contains: VideoProcessor, Transcript, Analyzer, Cutter, TitleGenerator
- Depends on: External libs (ffmpeg, faster-whisper, torch, LLM APIs)
- Used by: UI layer (VideoWorker)

**Config Layer:**
- Purpose: Application settings and API key management
- Location: `config/`
- Contains: settings.py (paths, defaults), llm_config.py (API keys)
- Depends on: Environment variables (.env)
- Used by: Core modules and UI

**Models Layer:**
- Purpose: Data structures
- Location: `models/`
- Contains: Profile
- Depends on: Pydantic
- Used by: UI, Core

## Data Flow

### Primary Request Path (Video Processing)

1. **User selects video** → `MainWindow._select_video()` (`ui/main_window.py:269`)
2. **User selects profile** → `MainWindow._load_profiles()` (`ui/main_window.py:217`)
3. **User clicks Process** → `MainWindow._process_video()` (`ui/main_window.py:277`)
4. **TitleConfigDialog shown** → User selects title mode → Returns to `_process_video()`
5. **VideoWorker.start()** → Background thread begins (`ui/main_window.py:297`)
6. **Pipeline in VideoWorker.run():**
   - `processor.get_video_info()` → FFmpeg probe for metadata (`ui/main_window.py:48`)
   - `Transcript.transcribe()` → Whisper audio-to-text (`ui/main_window.py:69`)
   - `Analyzer.extract_highlights()` → LLM extracts best segments (`ui/main_window.py:81`)
   - `Cutter.cut_video()` → FFmpeg cuts each highlight (`ui/main_window.py:98`)
   - `TitleGenerator.generate_title()` → AI generates titles (`ui/main_window.py:149`)
7. **Signals emitted** → Progress bar and log updated in UI
8. **finished signal** → Enable process button, show result message (`ui/main_window.py:303`)

### Profile Management Flow

1. **Load profiles** → `Profile.from_dict()` reads `profiles/default.json` (`models/profile.py:16`)
2. **Add/Edit profile** → `ProfileDialog` modal → `ProfileDialog.get_profile()` returns Profile
3. **Save profiles** → `MainWindow._save_profiles()` writes to JSON (`ui/main_window.py:262`)

**State Management:**
- UI state: `MainWindow` instance variables (`video_path`, `profiles`, `title_config`)
- Worker state: `VideoWorker` holds `video_path`, `profile`, `highlights`
- Persistent state: JSON file at `profiles/default.json`
- Debug state: `transcript_debug.json` in project root

## Key Abstractions

**Highlight (Pydantic Model):**
- Purpose: Represents an extracted video segment
- Examples: `core/analyzer.py:7`
- Pattern: Pydantic `BaseModel` with typed fields

**Profile (Pydantic Model):**
- Purpose: User-defined cutting configuration
- Examples: `models/profile.py:3`
- Pattern: Pydantic `BaseModel` with serialization via `to_dict()`/`from_dict()`

**VideoWorker (QThread):**
- Purpose: Background pipeline execution
- Examples: `ui/main_window.py:25`
- Pattern: Qt threading with pyqtSignal for progress/finish

## Entry Points

**main.py:**
- Location: `main.py`
- Triggers: `python main.py` or `./main.py`
- Responsibilities: Initialize Qt application, load environment, show MainWindow, start event loop

## Architectural Constraints

- **Threading:** Single QThread (VideoWorker) handles entire pipeline; main thread handles UI only
- **Global state:** Logging configured at module level in `ui/main_window.py:15`; `transcript_debug.json` written to cwd
- **Circular imports:** None detected — UI imports Core modules, but Core modules do not import UI
- **Blocking operations:** FFmpeg, Whisper, and LLM calls run in VideoWorker thread to avoid UI blocking

## Anti-Patterns

### Transcript saved to hardcoded path

**What happens:** `Transcript._save_transcript()` writes to `"transcript_debug.json"` in current working directory
**Why it's wrong:** File location is not configurable; may overwrite existing data or fail if cwd is different
**Do this instead:** Use `config.settings.OUTPUT_DIR / "transcript_debug.json"` — see `config/settings.py:7`

### Title generation method exists but is unused

**What happens:** `VideoWorker._generate_titles()` is defined at line 125 but only contains `pass`
**Why it's wrong:** Dead code; actual title generation happens inline in `run()` via `_get_title_suggestions()`
**Do this instead:** Remove `_generate_titles()` or implement it properly — see `ui/main_window.py:125`

### Hardcoded output filename pattern

**What happens:** `Cutter.cut_video()` uses `f"{input_path.stem}_{profile.name}_{index+1:03d}.mp4"` pattern
**Why it's wrong:** Not configurable; could cause filename collisions
**Do this instead:** Allow output name template configuration via Profile or settings

## Error Handling

**Strategy:** Logging + exception propagation with user-facing error messages

**Patterns:**
- `try/except` in `VideoWorker.run()` catches all exceptions and emits via `finished` signal with error message
- `logging.getLogger(__name__)` used consistently across core modules
- File operations use explicit checks (`path.exists()`, `check=True` on subprocess)

## Cross-Cutting Concerns

**Logging:** Python `logging` module configured in `ui/main_window.py` with both FileHandler (`sliceiq.log`) and StreamHandler
**Validation:** Pydantic models validate data at boundary (Profile, Highlight)
**Authentication:** API keys read from environment variables via `os.getenv()` in `config/llm_config.py`

---

*Architecture analysis: 2026-05-14*
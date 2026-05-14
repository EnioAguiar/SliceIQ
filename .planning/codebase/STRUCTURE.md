# Codebase Structure

**Analysis Date:** 2026-05-14

## Directory Layout

```
CortesVideos/
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (API keys)
├── .gitignore
├── sliceiq.log          # Runtime log file
├── transcript_debug.json # Debug transcript output
│
├── config/              # Configuration modules
│   ├── __init__.py
│   ├── settings.py      # App settings (paths, defaults)
│   └── llm_config.py   # LLM API key configuration
│
├── core/                # Video processing services
│   ├── __init__.py      # Barrel export: VideoProcessor, Transcript, Analyzer, Cutter
│   ├── analyzer.py      # Highlight extraction via LLM
│   ├── cutter.py        # FFmpeg video cutting
│   ├── transcript.py    # Whisper transcription
│   ├── video_processor.py # FFmpeg metadata extraction
│   └── title_generator.py # AI title generation
│
├── models/              # Data models
│   └── profile.py       # Profile Pydantic model
│
├── ui/                  # PyQt6 GUI components
│   ├── __init__.py
│   ├── main_window.py   # MainWindow + VideoWorker (QThread)
│   ├── profile_dialog.py # Profile editing dialog
│   ├── title_dialog.py  # Title generation config dialog
│   └── toast.py         # Toast notification widget
│
├── profiles/            # User data (persisted profiles)
│   └── default.json     # Default cutting profiles
│
├── output/              # Generated video clips
│   └── *.mp4            # Cut video segments
│
├── tests/               # Pytest test suite
│   ├── __init__.py
│   ├── test_analyzer.py
│   ├── test_video_processor.py
│   ├── test_profile.py
│   ├── test_title_generator.py
│   └── test_integration.py
│
├── venv/                # Virtual environment (not committed)
└── .planning/           # GSD planning artifacts
```

## Directory Purposes

**`ui/`:**
- Purpose: User interface components
- Contains: MainWindow (QMainWindow), dialogs (QDialog), ToastNotification
- Key files: `main_window.py` (308 lines), `title_dialog.py` (129 lines), `profile_dialog.py` (75 lines)

**`core/`:**
- Purpose: Video processing business logic
- Contains: VideoProcessor, Transcript, Analyzer, Cutter, TitleGenerator
- Key files: `analyzer.py` (149 lines), `title_generator.py` (138 lines), `transcript.py` (78 lines)

**`config/`:**
- Purpose: Application configuration and API key management
- Contains: settings.py (paths/directories), llm_config.py (API keys)
- Key files: `settings.py` (12 lines), `llm_config.py` (8 lines)

**`models/`:**
- Purpose: Data structure definitions
- Contains: Profile Pydantic model
- Key files: `profile.py` (17 lines)

**`tests/`:**
- Purpose: Unit and integration tests
- Contains: Tests for core modules, profile model
- Key files: `test_analyzer.py`, `test_video_processor.py`, `test_integration.py`

**`profiles/`:**
- Purpose: Persisted user profile data
- Contains: JSON files with cutting profiles
- Generated: Yes (by ProfileDialog save)

**`output/`:**
- Purpose: Cut video segments destination
- Contains: Generated MP4 files
- Generated: Yes (by Cutter.cut_video())

## Key File Locations

**Entry Points:**
- `main.py`: Application bootstrap — creates QApplication and MainWindow

**Configuration:**
- `config/settings.py`: Project paths, default model, CUDA device, Minimax mode
- `config/llm_config.py`: API keys (MINIMAX_API_KEY, GEMINI_API_KEY), provider list

**Core Logic:**
- `core/analyzer.py`: Highlight extraction via LLM (minimax/gemini/ollama/mock)
- `core/cutter.py`: FFmpeg video cutting with aspect ratio support
- `core/transcript.py`: Faster-Whisper transcription
- `core/video_processor.py`: FFmpeg metadata probing
- `core/title_generator.py`: AI title generation with templates

**UI Components:**
- `ui/main_window.py`: MainWindow class + VideoWorker (QThread)
- `ui/profile_dialog.py`: Profile creation/editing modal
- `ui/title_dialog.py`: Title mode selection (auto/template/custom)

**Models:**
- `models/profile.py`: Profile data model with Pydantic

## Naming Conventions

**Files:**
- Python modules: `lowercase_with_underscores.py` (e.g., `video_processor.py`)
- Dialog files: `*_dialog.py` (e.g., `profile_dialog.py`, `title_dialog.py`)
- Test files: `test_*.py` (e.g., `test_analyzer.py`)

**Classes:**
- PascalCase: `MainWindow`, `VideoWorker`, `ProfileDialog`, `TitleConfigDialog`
- Suffix patterns: `*Worker` (QThread), `*Dialog` (QDialog), `*Notification` (QWidget)

**Functions/Methods:**
- snake_case: `get_video_info()`, `extract_highlights()`, `cut_video()`
- Private methods: `_setup_ui()`, `_load_profiles()`, `_generate_titles()`

**Variables:**
- snake_case: `video_path`, `profile_list`, `title_config`
- Instance variables: `self.video_path`, `self.profiles`

**Types:**
- Pydantic models: `Profile`, `Highlight`
- Literal types: `"minimax"`, `"gemini"`, `"ollama"` in provider arguments

## Where to Add New Code

**New Feature:**
- Primary code: Add to `core/` as new module (e.g., `core/new_feature.py`)
- Import in `core/__init__.py` for barrel export
- UI integration: Add to `VideoWorker.run()` or create new dialog in `ui/`

**New Component/Module:**
- Implementation: Create new file in appropriate module directory
- Core logic → `core/`
- UI component → `ui/`
- Data model → `models/`

**Utilities:**
- Shared helpers: Consider adding to existing module if closely related, or create `utils.py` in `core/`

## Special Directories

**`.env`:**
- Purpose: Environment variables including API keys
- Generated: No (user creates)
- Committed: No (gitignored)

**`output/`:**
- Purpose: Cut video segments
- Generated: Yes (by Cutter.cut_video())
- Committed: No (gitignored)

**`profiles/`:**
- Purpose: Persisted cutting profiles
- Generated: Yes (by MainWindow._save_profiles())
- Committed: Yes (version controlled)

**`.planning/`:**
- Purpose: GSD planning artifacts
- Generated: Yes (by GSD commands)
- Committed: Yes (version controlled)

---

*Structure analysis: 2026-05-14*
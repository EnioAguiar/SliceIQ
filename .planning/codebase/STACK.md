# Technology Stack

**Analysis Date:** 2026-05-14

## Languages

**Primary:**
- Python 3.x - All application code (UI, core logic, config, tests)

**Secondary:**
- None detected

## Runtime

**Environment:**
- Python 3 with PyQt6 GUI application
- Virtual environment: `venv/` directory present

**Package Manager:**
- pip (requirements.txt)
- Lockfile: Not present (pip freeze not detected)

## Frameworks

**Core:**
- PyQt6>=6.6.0 - GUI framework for desktop application
- faster-whisper>=1.0.0 - Whisper-based transcription with GPU support
- torch>=2.0.0 - PyTorch for ML/AI operations
- torchvision>=0.15.0 - Computer vision utilities
- ffmpeg-python>=0.2.0 - FFmpeg integration for video processing
- pydantic>=2.0.0 - Data validation and settings management
- requests>=2.31.0 - HTTP client for API calls
- python-dotenv>=1.0.0 - Environment variable loading

**Testing:**
- pytest (implied by `tests/` directory and `.pytest_cache/`)
- unittest (standard library)

**Build/Dev:**
- None detected (no setup.py, pyproject.toml, or build tools)

## Key Dependencies

**Critical:**
- PyQt6 - GUI framework (`ui/main_window.py`, `ui/profile_dialog.py`, `ui/title_dialog.py`, `ui/toast.py`)
- faster-whisper - Speech-to-text transcription (`core/transcript.py`)
- torch - ML runtime with CUDA support (`core/transcript.py`, `core/analyzer.py`)
- pydantic - Settings and data models (`core/analyzer.py`, `config/settings.py`, `config/llm_config.py`)
- requests - HTTP client for LLM API calls (`core/analyzer.py`, `core/title_generator.py`)

**Infrastructure:**
- python-dotenv - Environment configuration (`.env` loading in `main.py`)
- ffmpeg-python - Video-to-audio conversion (`core/transcript.py`)

## Configuration

**Environment:**
- `.env` file with configuration
  - `MINIMAX_API_KEY` - Minimax AI API key (contains actual key)
  - `MINIMAX_MODE` - "token_plan" or "paygo"
  - `WHISPER_MODEL` - "medium"
- Environment variables loaded via `load_dotenv()` in `main.py`
- Settings class in `config/settings.py` with paths and CUDA device config

**Build:**
- No build configuration files detected (no pyproject.toml, setup.py, setup.cfg)
- Requirements only: `requirements.txt`

## Platform Requirements

**Development:**
- Python 3.x
- FFmpeg (external binary, used via subprocess in `core/transcript.py`)
- Virtual environment recommended

**Production:**
- Same as development
- FFmpeg must be installed on system
- CUDA-capable GPU recommended for faster transcription

---

*Stack analysis: 2026-05-14*
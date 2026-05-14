# Coding Conventions

**Analysis Date:** 2026-05-14

## Language

**Primary:**
- Python 3.11 - All application code

## Code Style

**Formatting:**
- No explicit formatter configured (no black, autopep8, etc.)
- Follow PEP 8 informally with 4-space indentation
- Line length not enforced

**Linting:**
- No explicit linter configured (no pylint, flake8, ruff, etc.)

**Import Organization:**
1. Standard library (`sys`, `os`, `pathlib`, `logging`, `json`, `re`, `random`)
2. Third-party packages (`PyQt6`, `pydantic`, `ffmpeg`, `requests`)
3. Local imports (`from ui.`, `from core.`, `from config.`, `from models.`)

**Path Aliases:** None used

## Naming Patterns

**Files:**
- lowercase_with_underscores: `video_processor.py`, `title_generator.py`
- test files prefixed with `test_`: `test_analyzer.py`

**Classes:**
- PascalCase: `Analyzer`, `VideoProcessor`, `TitleGenerator`, `Profile`
- Pydantic models: `Highlight`, `Profile`

**Functions/Methods:**
- snake_case: `extract_highlights`, `get_video_info`, `generate_title`
- Private methods prefixed with `_`: `_build_prompt`, `_call_llm`, `_parse_response`

**Variables:**
- snake_case: `transcript_text`, `video_path`, `sample_video`
- Constants: UPPER_SNAKE_CASE for module-level constants: `SUPPORTED_FORMATS`, `TEMPLATES`, `VARIABLES`, `MODES`

**Type Annotations:**
- Used in function signatures: `def extract_highlights(self, transcript_text: str, quantity: int = 5) -> list[Highlight]:`
- Used for class attributes where appropriate
- Literal types for provider selection: `Literal["minimax", "gemini", "ollama"]`

## Code Style Details

**Docstrings:** Not consistently used. Some functions have comments above explaining purpose.

**Comments:**
- Inline comments for non-obvious logic
- No consistent docstring format

**Function Design:**
- Functions tend to be focused, single-purpose
- Methods rarely exceed 50 lines
- Good use of early returns and guard clauses

**Class Design:**
- Pydantic `BaseModel` for data classes: `Highlight`, `Profile`
- Simple constructor patterns, no complex dependency injection

## Error Handling

**Patterns:**
- Exception raising with descriptive messages: `raise FileNotFoundError(f"Video not found: {video_path}")`
- Conditional checks with early returns in `core/analyzer.py` methods
- No try/except blocks in most code (exceptions propagate to caller)
- API calls do not always handle errors explicitly (assumes success or uses mock fallback)

**Logging:**
- Uses `logging.getLogger(__name__)` pattern
- Logger configured but no explicit handler setup visible in code
- Log calls: `logger.info(...)`, `logger.warning(...)`

**Validation:**
- Uses Pydantic for data model validation (`Profile`, `Highlight`)
- Runtime checks: `if mode not in self.MODES: raise ValueError(...)`

## Module Design

**Exports:**
- Package `__init__.py` files present: `core/__init__.py`, `models/__init__.py`, `ui/__init__.py`, `config/__init__.py`
- No explicit `__all__` defined

**Imports:**
- Relative imports: `from core.analyzer import Analyzer`
- No circular imports detected

---

*Convention analysis: 2026-05-14*
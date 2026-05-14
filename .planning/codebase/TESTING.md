# Testing Patterns

**Analysis Date:** 2026-05-14

## Test Framework

**Runner:**
- pytest >= 3.0 (discovered in tests)
- Config: No `pytest.ini`, `pyproject.toml`, or `setup.cfg` found

**Assertion Library:**
- pytest built-in assertions

**Run Commands:**
```bash
pytest                    # Run all tests
pytest -v                 # Verbose mode
pytest tests/             # Run specific directory
```

## Test File Organization

**Location:**
- `tests/` directory at project root, co-located with source
- Test files mirror source structure: `tests/test_analyzer.py` → `core/analyzer.py`

**Naming:**
- Pattern: `test_<module_name>.py`

**Structure:**
```
tests/
├── __init__.py
├── test_analyzer.py
├── test_video_processor.py
├── test_title_generator.py
├── test_profile.py
└── test_integration.py
```

## Test Structure

**Suite Organization:**
```python
import pytest
from module import ClassName

def test_functionality():
    # Arrange
    obj = ClassName()
    # Act
    result = obj.method()
    # Assert
    assert result == expected
```

**Patterns:**
- No formal test classes (uses function-based tests)
- Simple setup with direct instantiation
- Fixtures for shared objects

## Fixtures

**Defined in:** `tests/test_video_processor.py` and `tests/test_integration.py`

```python
@pytest.fixture
def processor():
    return VideoProcessor()

@pytest.fixture
def sample_video():
    return Path("tests/fixtures/sample.mp4")
```

**Standard Fixtures:**
- `processor` - VideoProcessor instance
- `sample_video` - Path to test video fixture
- `sample_profile` - Profile instance for integration tests

## Mocking

**Framework:** pytest's monkeypatch / manual mocking

**Patterns:**
- No explicit `unittest.mock` usage visible
- Mock provider pattern in `Analyzer` itself: `Analyzer(provider="mock")` returns deterministic fake highlights
- Conditional test skipping when fixtures missing: `if not sample_video.exists(): pytest.skip("No sample video")`

**What to Mock:**
- API calls (handled by "mock" provider in Analyzer)
- File system operations (use `pytest.skip` when files unavailable)

**What NOT to Mock:**
- Core business logic tested with real implementations
- Integration tests use real components with mock provider fallback

## Test Coverage Approach

**Current Test Files:**
- `test_analyzer.py` (22 lines) - Analyzer initialization, mock response, Highlight model
- `test_video_processor.py` (36 lines) - Format validation, file existence, video info extraction
- `test_title_generator.py` (32 lines) - Template loading, title generation in different modes
- `test_profile.py` (24 lines) - Profile creation, serialization (to_dict/from_dict)
- `test_integration.py` (40 lines) - Full pipeline from video to cut highlights

**Coverage Gaps:**
- `core/transcript.py` - Not tested directly
- `core/cutter.py` - Not tested directly
- `ui/` components - Not tested (PyQt6 GUI code)
- Error paths for API calls (network failures, invalid responses)
- Edge cases in LLM response parsing

## Test Types

**Unit Tests:**
- `test_profile.py` - Pure model serialization
- `test_analyzer.py` - Mock provider functionality
- `test_video_processor.py` - File validation logic

**Integration Tests:**
- `test_integration.py` - Full pipeline: video → transcript → analyze → cut

**E2E Tests:** Not used

## Common Patterns

**Async Testing:** Not applicable (synchronous code)

**Error Testing:**
```python
def test_get_video_info_missing_file(processor):
    with pytest.raises(FileNotFoundError):
        processor.get_video_info("nonexistent.mp4")
```

**Conditional Skip:**
```python
def test_get_video_info_with_fixture(sample_video):
    if not sample_video.exists():
        pytest.skip("No sample video")
```

**Fixture Availability Check:**
```python
@pytest.fixture
def sample_video():
    return Path("tests/fixtures/sample.mp4")
```

## Test Data

**Fixtures Location:** `tests/fixtures/` (referenced but may not exist in repo)

**Test Data Patterns:**
- Hardcoded sample values in tests
- Mock provider for deterministic test output
- No dedicated test data factories or fixtures module

---

*Testing analysis: 2026-05-14*
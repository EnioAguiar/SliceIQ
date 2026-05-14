# Codebase Concerns

**Analysis Date:** 2026-05-14

## Tech Debt

**Hardcoded file paths and magic strings:**
- Issue: `transcript_debug.json` is hardcoded in `core/transcript.py:72`, `core/analyzer.py:31`, `ui/main_window.py:60`, and `ui/main_window.py:140`. No configuration option to change location.
- Files: `core/transcript.py`, `core/analyzer.py`, `ui/main_window.py`
- Impact: Cannot use different transcripts for different videos, debug file pollutes working directory
- Fix approach: Add `TRANSCRIPT_PATH` to `config/settings.py`, pass through transcript context

**API key validation silent fallback:**
- Issue: When `MINIMAX_API_KEY` is missing, the system silently uses mock responses (`core/analyzer.py:67-68`, `core/title_generator.py:103-105`). No user warning.
- Files: `core/analyzer.py`, `core/title_generator.py`
- Impact: Users may not realize their AI analysis is using fake/random data instead of real LLM calls
- Fix approach: Add warning log and UI notification when API key is missing

**Empty list return on parse failure:**
- Issue: `_parse_response` in `core/analyzer.py:143-149` returns empty list when JSON parsing fails. No error logged.
- Files: `core/analyzer.py`
- Impact: Silently fails to extract highlights, user sees no error but gets no results
- Fix approach: Log warning with response snippet on parse failure

**Unused `_generate_titles` method:**
- Issue: `ui/main_window.py:125-126` defines `_generate_titles` as empty pass, while actual title logic is in `_get_title_suggestions`
- Files: `ui/main_window.py`
- Impact: Dead code, confusion about which method is used
- Fix approach: Remove unused method

**Global logging configuration:**
- Issue: `ui/main_window.py:15-22` configures logging at module import time with `logging.basicConfig`, overwriting any parent application logging config
- Files: `ui/main_window.py`
- Impact: Hard to integrate with larger applications that need custom logging
- Fix approach: Use `logging.getLogger()` and configure via parent, or use dictConfig

**Title config dialog always shown even if canceled:**
- Issue: `ui/main_window.py:286-290` shows `TitleConfigDialog` but processing continues regardless of whether user confirmed or canceled (dialog.exec() returning False still proceeds)
- Files: `ui/main_window.py`
- Impact: User cannot skip title generation without selecting something in the dialog
- Fix approach: Check dialog result before proceeding

## Known Bugs

**Transcript segment text matching is loose:**
- Issue: In `ui/main_window.py:143`, segment text is matched with `seg["start"] >= h.start - 1 and seg["end"] <= h.end + 1`. The `end` condition could miss segments that start within the range but end outside it.
- Files: `ui/main_window.py`
- Trigger: Highlights where segments cross the boundary
- Workaround: None

**FFmpeg eval injection risk:**
- Issue: `core/video_processor.py:30` uses `eval(video_stream["r_frame_rate"])` on untrusted ffmpeg output
- Files: `core/video_processor.py`
- Trigger: Malicious video file with crafted stream metadata
- Workaround: Avoid processing untrusted video sources

**No ffmpeg path validation:**
- Issue: `core/cutter.py` and `core/video_processor.py` assume ffmpeg is in PATH. No error handling if missing.
- Files: `core/cutter.py`, `core/video_processor.py`
- Trigger: Environment without ffmpeg installed
- Workaround: Install ffmpeg before running

**Temp file leak on subprocess failure:**
- Issue: In `core/transcript.py:32-40`, if `subprocess.run` fails, the tempfile created at line 33 is not cleaned up
- Files: `core/transcript.py`
- Trigger: Corrupt video file causing ffmpeg to fail
- Workaround: None

## Security Considerations

**API keys in environment variables read at module import:**
- Risk: `config/llm_config.py` reads API keys at import time. If the module is imported in a context where env vars aren't set, no error occurs — just silent failure.
- Files: `config/llm_config.py`, `config/settings.py`
- Current mitigation: None
- Recommendations: Add validation on first use rather than import, raise clear error if key missing when actually needed

**No input validation on video path:**
- Risk: `core/video_processor.py:10-13` checks file existence but doesn't validate path traversal risks
- Files: `core/video_processor.py`
- Current mitigation: `Path.exists()` handles some cases
- Recommendations: Use `Path.resolve()` and validate result is within expected directory

**Hardcoded output directory:**
- Risk: `core/cutter.py:14` creates `output` dir, no protection against symlink attacks or path traversal
- Files: `core/cutter.py`
- Current mitigation: `parents=True` but no real path validation
- Recommendations: Resolve output path before creation

## Performance Bottlenecks

**Whisper model loaded for every video:**
- Problem: `core/transcript.py:24-30` loads Whisper model in `load_model()`. If processing multiple videos sequentially, model is reloaded or kept in memory with no reuse strategy.
- Files: `core/transcript.py`
- Cause: Transcript instance created per-video in `VideoWorker.run()`
- Improvement path: Create a singleton model manager that shares model across Transcript instances

**JSON parsing on every prompt:**
- Problem: `core/analyzer.py:29-30` imports `json` and `Path` inside `_build_prompt` method, called on every highlight extraction
- Files: `core/analyzer.py`
- Cause: Imports inside method
- Improvement path: Move imports to module level

**Title generator instantiated per highlight:**
- Problem: In `ui/main_window.py:131`, `TitleGenerator("auto", {})` is created once but used in a loop. Could be created once outside loop.
- Files: `ui/main_window.py`
- Cause: Created before loop but never reused across different title modes
- Improvement path: Pass generator instance through methods

**No caching of transcript results:**
- Problem: Transcript is re-computed if `transcript_debug.json` is deleted. No caching mechanism beyond that single file.
- Files: `core/transcript.py`
- Cause: Simple file-based caching with no TTL or content-addressable storage
- Improvement path: Add content-hash based cache with video hash as key

## Fragile Areas

**Hardcoded Minimax API endpoints:**
- Files: `core/analyzer.py:74-78`, `core/title_generator.py:111-115`
- Why fragile: API URLs hardcoded; if Minimax changes endpoint, code breaks with no configuration option
- Safe modification: Extract to `config/llm_config.py` as constants
- Test coverage: Only tested with mock provider

**Profile loading fails silently:**
- Files: `ui/main_window.py:217-228`
- Why fragile: If `default.json` is malformed, the error is not caught. No validation of profile data against Profile model.
- Safe modification: Wrap in try/except, add validation
- Test coverage: No test for malformed profile file

**Cutter output filename collision:**
- Files: `core/cutter.py:36`
- Why fragile: Output name uses `{stem}_{profile}_{index:03d}.mp4`. If two profiles have same name, files overwrite.
- Safe modification: Add timestamp or uuid to guarantee uniqueness
- Test coverage: None

## Scaling Limits

**Memory: Large video files:**
- Current capacity: No streaming — full video info via `ffmpeg.probe`
- Limit: Videos larger than available RAM may cause OOM
- Scaling path: Stream processing or chunked probe

**Storage: No cleanup of output directory:**
- Current capacity: Output dir grows indefinitely
- Limit: Disk full
- Scaling path: Add cleanup policy or output to dated subdirectories

**Processing: Sequential highlight cutting:**
- Current capacity: Highlights cut one at a time in `ui/main_window.py:95-98`
- Limit: Many highlights = slow total time
- Scaling path: Parallel ffmpeg processes for independent clips

## Dependencies at Risk

**faster-whisper:**
- Risk: Heavy ML dependency with CUDA compatibility windows
- Impact: Model load fails if torch version incompatible
- Migration plan: Could fallback to openai-whisper or huggingface transformers

**ffmpeg-python:**
- Risk: Thin wrapper around ffmpeg CLI. If ffmpeg binary missing, obscure errors.
- Impact: `ffmpeg.run()` fails with cryptic messages
- Migration plan: Could replace with direct subprocess calls for better error handling

## Missing Critical Features

**Error recovery:**
- Problem: If any step fails (transcription, analysis, cutting), no retry logic
- Blocks: Production use where failures are common (network, corrupt files)

**Progress for title generation:**
- Problem: Title generation happens after progress hits 85%, no individual clip progress shown
- Blocks: User understanding of what happened if titles fail

**Video format auto-detection:**
- Problem: User must select correct format in profile; no auto-detection from video metadata
- Blocks: Easy profile setup

## Test Coverage Gaps

**No tests for API clients:**
- What's not tested: `_call_minimax`, `_call_gemini`, `_call_ollama` methods
- Files: `core/analyzer.py`
- Risk: API changes silently break functionality
- Priority: Medium

**No tests for VideoProcessor error paths:**
- What's not tested: `get_video_info` with missing file, invalid video
- Files: `core/video_processor.py`
- Risk: Errors surface as cryptic ffmpeg errors rather than clear Python exceptions
- Priority: Medium

**No tests for Cutter:**
- What's not tested: `cut_video` method entirely
- Files: `core/cutter.py`
- Risk: Cutting logic silently fails or produces invalid output
- Priority: High

**No tests for TitleGenerator:**
- What's not tested: `_generate_auto`, `_generate_template`, `_generate_custom`, `_call_minimax`
- Files: `core/title_generator.py`
- Risk: Title generation breaks without detection
- Priority: Medium

**No tests for profile serialization roundtrip:**
- What's not tested: `Profile.to_dict` and `Profile.from_dict` with all field types
- Files: `models/profile.py`
- Risk: Profile save/load corruption
- Priority: Low

**No UI tests:**
- What's not tested: Dialog interactions, worker thread signals, profile list operations
- Files: `ui/main_window.py`, `ui/profile_dialog.py`, `ui/title_dialog.py`
- Risk: UI regressions undetected
- Priority: High

---

*Concerns audit: 2026-05-14*
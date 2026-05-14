# External Integrations

**Analysis Date:** 2026-05-14

## APIs & External Services

**AI/LLM Providers:**
- **Minimax API** - Primary LLM provider for title generation and highlight extraction
  - SDK/Client: `requests` library (manual HTTP calls)
  - Auth: `MINIMAX_API_KEY` env var
  - Endpoints used:
    - `https://api.minimax.io/anthropic/v1/messages` (token_plan mode)
    - `https://api.minimax.chat/v1/text/chatcompletion_v2` (paygo mode)
  - Models: `MiniMax-M2.7` (token_plan), `minimax-01` (paygo)
  - Files: `core/analyzer.py`, `core/title_generator.py`

- **Google Gemini API** - Alternative LLM provider
  - SDK/Client: `requests` library (manual HTTP calls)
  - Auth: `GEMINI_API_KEY` env var
  - Endpoint: `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent`
  - File: `core/analyzer.py`

- **Ollama (local)** - Self-hosted LLM alternative
  - SDK/Client: `requests` library
  - Endpoint: `http://localhost:11434/api/chat`
  - Model: `llama3` (hardcoded)
  - File: `core/analyzer.py`

## Data Storage

**Databases:**
- None detected (no SQLite, PostgreSQL, etc.)

**File Storage:**
- Local filesystem only
  - Profiles: `profiles/` directory
  - Output: `output/` directory
  - Transcript debug: `transcript_debug.json` (generated at project root)
  - Video files processed from user-selected paths

**Caching:**
- None detected (no Redis, Memcached, etc.)

## Authentication & Identity

**Auth Provider:**
- API keys managed via environment variables
- No user authentication system implemented
- `.env` file contains sensitive API keys (should not be committed)

## Monitoring & Observability

**Error Tracking:**
- None detected (no Sentry, Bugsnag, etc.)

**Logs:**
- Python `logging` module used in several files
  - `core/transcript.py`, `core/analyzer.py`, `core/title_generator.py`
  - `sliceiq.log` file present in project root
  - Console and file handlers likely configured

## CI/CD & Deployment

**Hosting:**
- None detected (no cloud deployment configurations)

**CI Pipeline:**
- None detected

## Environment Configuration

**Required env vars:**
- `MINIMAX_API_KEY` - Minimax API authentication (required for AI features)
- `MINIMAX_MODE` - "token_plan" or "paygo" (defaults to "paygo")
- `WHISPER_MODEL` - Whisper model size (defaults to "medium")
- `GEMINI_API_KEY` - Google Gemini API (optional, for alternative LLM)

**Secrets location:**
- `.env` file at project root
- Loaded via `python-dotenv` in `main.py`

## Webhooks & Callbacks

**Incoming:**
- None detected

**Outgoing:**
- None detected

## External Binaries

**FFmpeg:**
- Used for video-to-audio conversion
- Called via `subprocess.run()` in `core/transcript.py`
- Must be installed on system PATH
- Command: `ffmpeg -y -i {video} -ar 16000 -ac 1 -acodec pcm_s16le {output.wav}`

---

*Integration audit: 2026-05-14*
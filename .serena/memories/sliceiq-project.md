# SliceIQ - Projeto

## Overview
Ferramenta desktop Linux para cortar vídeos longos do YouTube em highlights automaticamente usando IA.

**GitHub:** https://github.com/EnioAguiar/SliceIQ

## Stack
- Python 3.11 + venv
- PyQt6 (UI desktop)
- FFmpeg (processamento vídeo)
- Faster-Whisper (transcrição CPU)
- LLM: MiniMax-M2.7 (Token Plan)

## Pipeline Funcional
1. Transcript com timestamps (Whisper CPU, salva em transcript_debug.json)
2. Analyzer (Minimax real via /anthropic/v1/messages)
3. Cutter (FFmpeg, ajusta duration se fora do range)
4. TitleGenerator (Minimax gera títulos, 3 modos: Auto/Template/Custom)

## Estrutura
```
SliceIQ/
├── main.py                    # Entry point com encoding fix
├── core/
│   ├── video_processor.py
│   ├── transcript.py          # Salva transcript_debug.json
│   ├── analyzer.py            # Minimax Token Plan
│   ├── cutter.py              # Ajusta duration
│   └── title_generator.py     # Título com prefixos
├── ui/
│   ├── main_window.py        # QThread worker, TitleConfigDialog
│   ├── profile_dialog.py
│   ├── title_dialog.py       # Wizard 3 etapas
│   └── toast.py             # Notificação
├── models/profile.py
├── config/settings.py         # MINIMAX_MODE token_plan/paygo
└── profiles/default.json
```

## Environment Variables (.env)
```
MINIMAX_API_KEY=sk-cp-xxx
MINIMAX_MODE=token_plan
WHISPER_MODEL=medium
```

## Status Atual
- CPU mode (GPU unavailable)
- UI não congela (QThread)
- Perfil add/edit/remove funcionando
- Minimax Token Plan configurado
- Title generation com template prefixes
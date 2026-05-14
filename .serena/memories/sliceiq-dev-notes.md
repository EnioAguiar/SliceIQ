# SliceIQ Development Notes

## Current State (v1 MVP)
- Pipeline funcional: Transcript → Analyzer (Minimax) → Cutter → TitleGenerator
- UI com PyQt6 com multi-profile, add/edit/remove perfis funcionando
- Thread worker para UI responsiva (não congela)
- Logs em sliceiq.log e transcript_debug.json
- Title generation (Auto/Template/Custom) com Minimax

## To Do
- Implementar crop/convert para 9:16, 1:1 (futuro)
- Face tracking com MediaPipe (futuro)
- Preview dos cortes
- Testar com vídeos longos (1.5h)

## Commands
```bash
cd /home/enio/CortesVideos
python3 -m venv venv
source venv/bin/activate
python3 main.py
tail -f sliceiq.log
```

## Running Tests
```bash
source venv/bin/activate
python -m pytest tests/ -v
```

## Files
- `transcript_debug.json` - Salvado após transcrição com timestamps
- `sliceiq.log` - Logs de execução
- `output/` - Onde ficam os cortes gerados

## Profiles
- TikTok Short: 15-30s
- YouTube Normal: 45-120s
- YouTube Video: 300-600s (para cortes maiores)
import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QListWidget, QPushButton, QProgressBar, QTextEdit,
    QLabel, QFileDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from ui.toast import ToastNotification
from ui.title_dialog import TitleConfigDialog
from core.title_generator import TitleGenerator

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sliceiq.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class VideoWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)

    def __init__(self, video_path, profile, title_mode=None, title_config=None):
        super().__init__()
        self.video_path = video_path
        self.profile = profile
        self.title_mode = title_mode
        self.title_config = title_config or {}
        self.highlights = []

    def run(self):
        try:
            logger.info("=== INICIANDO PROCESSAMENTO ===")
            self.progress.emit(10, "Importando módulos...")

            from core import VideoProcessor, Transcript, Analyzer, Cutter

            processor = VideoProcessor()
            self.progress.emit(20, "Verificando vídeo...")
            logger.info(f"Vídeo: {self.video_path}")

            info = processor.get_video_info(self.video_path)
            logger.info(f"Duração: {info['duration']:.1f}s")
            self.progress.emit(30, f"Duração: {info['duration']:.1f}s")

            self.progress.emit(35, "Carregando modelo Whisper...")
            logger.info("Carregando Transcript...")
            transcript = Transcript()

            self.progress.emit(40, "Transcrevendo áudio (isso pode levar minutos)...")
            logger.info("Iniciando transcrição...")

            from pathlib import Path
            transcript_file = Path("transcript_debug.json")
            if transcript_file.exists():
                self.progress.emit(50, "Usando transcript existente...")
                logger.info("Transcript já existe, pulando transcrição")
                with open(transcript_file, "r", encoding="utf-8") as f:
                    import json
                    data = json.load(f)
                    text = data.get("full_text", "")
            else:
                text = transcript.get_full_text(self.video_path)
                logger.info(f"Transcript completo: {len(text)} caracteres")
                self.progress.emit(50, f"Transcrição feita: {len(text)} caracteres")

            self.progress.emit(55, "Carregando Analyzer...")
            logger.info("Carregando Analyzer...")
            from config.llm_config import LLMConfig
            provider = "minimax" if LLMConfig.MINIMAX_API_KEY else "mock"
            analyzer = Analyzer(provider=provider)

            self.progress.emit(60, "Extraindo highlights...")
            logger.info("Extraindo highlights...")
            self.highlights = analyzer.extract_highlights(
                text,
                quantity=self.profile.quantity,
                duration_min=self.profile.duration_min,
                duration_max=self.profile.duration_max
            )
            logger.info(f"Encontrados {len(self.highlights)} highlights")
            self.progress.emit(70, f"Encontrados {len(self.highlights)} highlights")

            self.progress.emit(75, "Preparando cutter...")
            logger.info("Preparando cutter...")
            cutter = Cutter()

            self.progress.emit(80, "Cortando vídeo...")
            for i, h in enumerate(self.highlights):
                logger.info(f"Cortando highlight {i+1}: {h.start:.1f}s - {h.end:.1f}s (score: {h.score})")
                self.progress.emit(80 + (i * 20 // len(self.highlights)), f"Cortando highlight {i+1}/{len(self.highlights)}")
                cutter.cut_video(self.video_path, h.start, h.end, self.profile, index=i)

            # Generate titles
            title_suggestions = {}
            if self.title_mode:
                clip_files = sorted(Path("output").glob("*.mp4"))
                self.progress.emit(85, "Gerando títulos...")
                title_suggestions = self._get_title_suggestions(clip_files)

            self.progress.emit(100, "Concluído!")
            logger.info("=== PROCESSAMENTO CONCLUÍDO ===")

            result_msg = f"Sucesso! {len(self.highlights)} clips gerados"
            if title_suggestions:
                result_msg += f"\n\n=== SUGESTÕES DE TÍTULOS ===\n"
                for clip_path, suggestions in title_suggestions.items():
                    clip_name = clip_path.name
                    result_msg += f"\n📁 {clip_name}\n"
                    for i, sug in enumerate(suggestions, 1):
                        result_msg += f"   {i}. {sug}\n"

            self.finished.emit(True, result_msg)

        except Exception as e:
            logger.error(f"ERRO: {e}", exc_info=True)
            self.finished.emit(False, f"Erro: {str(e)}")

    def _generate_titles(self):
        pass

    def _get_title_suggestions(self, clip_files: list) -> dict:
        import json
        from pathlib import Path
        generator = TitleGenerator("auto", {})

        suggestions = {}
        for i, clip in enumerate(clip_files):
            if i >= len(self.highlights):
                break

            h = self.highlights[i]
            segment_text = ""
            with open("transcript_debug.json", "r", encoding="utf-8") as f:
                transcript_data = json.load(f)
                for seg in transcript_data.get("segments", []):
                    if seg["start"] >= h.start - 1 and seg["end"] <= h.end + 1:
                        segment_text += seg["text"] + " "

            clip_suggestions = []
            for _ in range(1):
                try:
                    title = generator.generate_title(
                        highlight_text=segment_text.strip(),
                        start=h.start,
                        end=h.end,
                        duration=h.end - h.start
                    )
                    if title and title not in clip_suggestions:
                        clip_suggestions.append(title)
                except Exception as e:
                    logger.error(f"Erro ao gerar título para {clip.name}: {e}")

            suggestions[clip] = clip_suggestions

        return suggestions


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CortesVideos")
        self.setMinimumSize(800, 600)

        self.video_path = None
        self.profiles = []
        self.toast = ToastNotification()
        self.title_config = None

        self._setup_ui()
        self._load_profiles()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.profile_list = QListWidget()
        layout.addWidget(QLabel("Perfis de Corte"))
        layout.addWidget(self.profile_list)

        buttons = QWidget()
        btn_layout = QVBoxLayout(buttons)

        self.btn_add_profile = QPushButton("Adicionar Perfil")
        self.btn_edit_profile = QPushButton("Editar Perfil")
        self.btn_remove_profile = QPushButton("Remover Perfil")
        self.btn_select_video = QPushButton("Selecionar Vídeo")
        self.btn_process = QPushButton("Processar")
        self.btn_ai_workflow = QPushButton("AI Workflow")

        for btn in [self.btn_add_profile, self.btn_edit_profile,
                    self.btn_remove_profile, self.btn_select_video, self.btn_process, self.btn_ai_workflow]:
            btn_layout.addWidget(btn)

        layout.addWidget(buttons)

        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(QLabel("Log"))
        layout.addWidget(self.log)

        self.btn_add_profile.clicked.connect(self._add_profile)
        self.btn_edit_profile.clicked.connect(self._edit_profile)
        self.btn_remove_profile.clicked.connect(self._remove_profile)
        self.btn_select_video.clicked.connect(self._select_video)
        self.btn_process.clicked.connect(self._process_video)
        self.btn_ai_workflow.clicked.connect(self._open_ai_workflow)

    def _load_profiles(self):
        from models.profile import Profile
        import json
        from config.settings import settings

        profile_file = settings.PROFILES_DIR / "default.json"
        if profile_file.exists():
            with open(profile_file) as f:
                data = json.load(f)
                for p in data.get("profiles", []):
                    self.profiles.append(Profile.from_dict(p))
                    self.profile_list.addItem(p["name"])

    def _add_profile(self):
        from ui.profile_dialog import ProfileDialog
        dialog = ProfileDialog()
        if dialog.exec():
            profile = dialog.get_profile()
            self.profiles.append(profile)
            self.profile_list.addItem(profile.name)
            self._save_profiles()

    def _edit_profile(self):
        idx = self.profile_list.currentRow()
        if idx < 0:
            return

        from ui.profile_dialog import ProfileDialog
        dialog = ProfileDialog(self.profiles[idx])
        if dialog.exec():
            self.profiles[idx] = dialog.get_profile()
            self.profile_list.item(idx).setText(dialog.get_profile().name)
            self._save_profiles()

    def _remove_profile(self):
        idx = self.profile_list.currentRow()
        if idx < 0:
            self.log.append("Selecione um perfil para remover")
            return
        self.log.append(f"Removendo perfil: {self.profiles[idx].name}")
        self.profiles.pop(idx)
        self.profile_list.takeItem(idx)
        self._save_profiles()
        self.log.append("Perfil removido")

    def _save_profiles(self):
        import json
        from config.settings import settings
        data = {"profiles": [p.to_dict() for p in self.profiles]}
        with open(settings.PROFILES_DIR / "default.json", "w") as f:
            json.dump(data, f, indent=2)

    def _select_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Vídeo", "", "Video Files (*.mp4 *.mkv *.mov)"
        )
        if file_path:
            self.video_path = file_path
            self.log.append(f"Vídeo selecionado: {file_path}")

    def _process_video(self):
        if not self.video_path:
            self.log.append("Selecione um vídeo primeiro")
            return

        if self.profile_list.currentRow() < 0:
            self.log.append("Selecione um perfil primeiro")
            return

        dialog = TitleConfigDialog()
        if not dialog.exec():
            return

        mode, self.title_config = dialog.get_config()
        self.log.clear()
        self.log.append(f"Iniciando processamento (modo título: {mode})...")
        self.progress.setValue(0)
        self.btn_process.setEnabled(False)

        profile = self.profiles[self.profile_list.currentRow()]
        self.worker = VideoWorker(self.video_path, profile, mode, self.title_config)

        self.worker.progress.connect(lambda val, msg: (
            self.progress.setValue(val),
            self.log.append(msg)
        ))
        self.worker.finished.connect(lambda ok, msg: (
            self.log.append(msg),
            self.btn_process.setEnabled(True)
        ))

        self.worker.start()

    def _open_ai_workflow(self):
        from ui.workflow_dialog import WorkflowDialog
        if not self.video_path:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Video", "Please select a video first")
            return
        dialog = WorkflowDialog(self.video_path, self)
        dialog.exec()
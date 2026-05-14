import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QListWidget, QPushButton, QProgressBar, QTextEdit,
    QLabel, QFileDialog
)
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CortesVideos")
        self.setMinimumSize(800, 600)

        self.video_path = None
        self.profiles = []

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

        for btn in [self.btn_add_profile, self.btn_edit_profile,
                    self.btn_remove_profile, self.btn_select_video, self.btn_process]:
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

    def _edit_profile(self):
        pass

    def _remove_profile(self):
        pass

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

        self.log.append("Iniciando processamento...")
        self.progress.setValue(10)

        from core import VideoProcessor, Transcript, Analyzer, Cutter
        from models.profile import Profile

        processor = VideoProcessor()
        self.progress.setValue(20)

        info = processor.get_video_info(self.video_path)
        self.log.append(f"Duração: {info['duration']:.1f}s")

        self.progress.setValue(30)

        transcript = Transcript()
        text = transcript.get_full_text(self.video_path)
        self.log.append(f"Transcript completo: {len(text)} caracteres")

        self.progress.setValue(50)

        analyzer = Analyzer(provider="mock")
        selected_profile = self.profiles[self.profile_list.currentRow()]

        highlights = analyzer.extract_highlights(
            text,
            quantity=selected_profile.quantity,
            duration_min=selected_profile.duration_min,
            duration_max=selected_profile.duration_max
        )

        self.log.append(f"Encontrados {len(highlights)} highlights")

        self.progress.setValue(70)

        cutter = Cutter()
        for i, h in enumerate(highlights):
            self.log.append(f"Cortando highlight {i+1}: {h.start:.1f}s - {h.end:.1f}s (score: {h.score})")
            cutter.cut_video(self.video_path, h.start, h.end, selected_profile)

        self.progress.setValue(100)
        self.log.append("Processamento completo!")
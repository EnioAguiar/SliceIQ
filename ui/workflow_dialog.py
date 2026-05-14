import sys
import json
import logging
from pathlib import Path
from enum import Enum

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget, QLabel,
    QPushButton, QProgressBar, QTextEdit, QLineEdit,
    QListWidget, QListWidgetItem, QAbstractItemView,
    QCheckBox, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QSizePolicy, QSpacerItem,
    QApplication
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QColor, QPalette, QFont

from core.workflow import VideoClippingWorkflow, WorkflowStage
from models.profile import Profile
from models.highlight import ScoredHighlight

logger = logging.getLogger(__name__)


STYLESHEET_DARK = """
QDialog {
    background-color: #1F2937;
    color: #F9FAFB;
}
QLabel {
    color: #F9FAFB;
}
QPushButton {
    background-color: #374151;
    color: #F9FAFB;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    min-width: 80px;
}
QPushButton:hover {
    background-color: #4B5563;
}
QPushButton:pressed {
    background-color: #6366F1;
}
QPushButton:disabled {
    background-color: #1F2937;
    color: #6B7280;
}
QPushButton.primary {
    background-color: #6366F1;
    color: white;
}
QPushButton.primary:hover {
    background-color: #818CF8;
}
QPushButton.success {
    background-color: #22C55E;
    color: white;
}
QLineEdit {
    background-color: #374151;
    color: #F9FAFB;
    border: 1px solid #4B5563;
    border-radius: 4px;
    padding: 8px;
}
QLineEdit:focus {
    border-color: #6366F1;
}
QListWidget {
    background-color: #374151;
    color: #F9FAFB;
    border: 1px solid #4B5563;
    border-radius: 4px;
}
QListWidget::item:selected {
    background-color: #6366F1;
}
QTableWidget {
    background-color: #374151;
    color: #F9FAFB;
    border: 1px solid #4B5563;
    border-radius: 4px;
    gridline-color: #4B5563;
}
QTableWidget::item:selected {
    background-color: #6366F1;
}
QHeaderView::section {
    background-color: #374151;
    color: #F9FAFB;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #6366F1;
}
QCheckBox {
    color: #F9FAFB;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 3px;
    border: 2px solid #6366F1;
}
QCheckBox::indicator:checked {
    background-color: #6366F1;
}
QProgressBar {
    background-color: #374151;
    border: none;
    border-radius: 4px;
    text-color: #F9FAFB;
}
QProgressBar::chunk {
    background-color: #6366F1;
    border-radius: 4px;
}
QFrame.card {
    background-color: #374151;
    border-radius: 8px;
    border: 1px solid #4B5563;
}
"""


class Stage(Enum):
    UPLOAD = 1
    ANALYZE = 2
    REVIEW = 3
    CONFIGURE = 4
    EXPORT = 5


class WorkflowDialog(QDialog):
    def __init__(self, video_path=None, parent=None):
        super().__init__(parent)
        self.video_path = video_path
        self.profiles = []
        self.selected_profiles = []
        self.highlights = []
        self.scored_highlights = []
        self.workflow_id = None
        self.current_stage = Stage.UPLOAD
        self._load_profiles()
        self._setup_ui()
        self.setStyleSheet(STYLESHEET_DARK)
        self.setMinimumSize(900, 650)

    def _load_profiles(self):
        from config.settings import settings
        profile_file = settings.PROFILES_DIR / "default.json"
        if profile_file.exists():
            with open(profile_file) as f:
                data = json.load(f)
                for p in data.get("profiles", []):
                    self.profiles.append(Profile.from_dict(p))

    def _setup_ui(self):
        self.setWindowTitle("AI Workflow - CortesVideos")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        layout.addWidget(self._create_stage_progress())
        layout.addWidget(self._create_content_area())
        layout.addWidget(self._create_button_bar())

    def _create_stage_progress(self):
        container = QFrame()
        container.setFrameStyle(QFrame.Shape.NoFrame)
        container.setObjectName("card")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        self.stage_labels = []
        stages = ["Upload", "Analyze", "Review", "Configure", "Export"]
        for i, name in enumerate(stages, 1):
            stage_layout = QVBoxLayout()
            stage_layout.setSpacing(4)
            stage_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            circle = QLabel("●" if i > 1 else "●")
            circle.setAlignment(Qt.AlignmentFlag.AlignCenter)
            circle.setStyleSheet(f"color: {'#6366F1' if i == 1 else '#22C55E' if i < 1 else '#6B7280'}; font-size: 24px;")
            circle.setProperty("stage", i)

            label = QLabel(name)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet(f"color: {'#6366F1' if i == 1 else '#22C55E' if i < 1 else '#6B7280'}; font-weight: {'bold' if i == 1 else 'normal'};")
            label.setProperty("stage", i)

            self.stage_labels.append((circle, label))
            stage_layout.addWidget(circle)
            stage_layout.addWidget(label)
            layout.addLayout(stage_layout)

            if i < 5:
                line = QLabel("─")
                line.setStyleSheet("color: #4B5563; font-size: 20px;")
                layout.addWidget(line)

        return container

    def _create_content_area(self):
        self.content_stack = QWidget()
        self.content_layout = QVBoxLayout(self.content_stack)

        self.upload_widget = self._create_upload_widget()
        self.analyze_widget = self._create_analyze_widget()
        self.review_widget = self._create_review_widget()
        self.configure_widget = self._create_configure_widget()
        self.export_widget = self._create_export_widget()

        self.content_layout.addWidget(self.upload_widget)
        self.content_layout.addWidget(self.analyze_widget)
        self.content_layout.addWidget(self.review_widget)
        self.content_layout.addWidget(self.configure_widget)
        self.content_layout.addWidget(self.export_widget)

        self._show_stage(Stage.UPLOAD)
        return self.content_stack

    def _create_upload_widget(self):
        widget = QFrame()
        widget.setObjectName("card")
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        title = QLabel("Upload Video")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #F9FAFB;")
        layout.addWidget(title)

        layout.addWidget(QLabel("YouTube URL:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://www.youtube.com/watch?v=...")
        layout.addWidget(self.url_input)

        self.url_preview = QLabel("No video selected")
        self.url_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.url_preview.setStyleSheet("color: #6B7280;")
        self.url_preview.setMinimumHeight(120)
        self.url_preview.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        layout.addWidget(self.url_preview)

        return widget

    def _create_analyze_widget(self):
        widget = QFrame()
        widget.setObjectName("card")
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        title = QLabel("Analyzing Video")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #F9FAFB;")
        layout.addWidget(title)

        self.analyze_progress = QProgressBar()
        self.analyze_progress.setRange(0, 100)
        self.analyze_progress.setValue(0)
        layout.addWidget(self.analyze_progress)

        self.analyze_status = QLabel("Initializing...")
        self.analyze_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.analyze_status)

        self.analyze_substages = QLabel("Stage: Loading")
        self.analyze_substages.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.analyze_substages.setStyleSheet("color: #6B7280;")
        layout.addWidget(self.analyze_substages)

        layout.addStretch()
        return widget

    def _create_review_widget(self):
        widget = QFrame()
        widget.setObjectName("card")
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        title = QLabel("Review Highlights")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #F9FAFB;")
        layout.addWidget(title)

        self.highlights_table = QTableWidget()
        self.highlights_table.setColumnCount(6)
        self.highlights_table.setHorizontalHeaderLabels(["#", "Timestamp", "Duration", "Hook", "Viral", "Total"])
        self.highlights_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.highlights_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.highlights_table.verticalHeader().setVisible(False)
        self.highlights_table.setAlternatingRowColors(True)

        header = self.highlights_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.highlights_table)

        info = QLabel("Click on rows to select/deselect highlights for processing")
        info.setStyleSheet("color: #6B7280; font-size: 12px;")
        layout.addWidget(info)

        return widget

    def _create_configure_widget(self):
        widget = QFrame()
        widget.setObjectName("card")
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        title = QLabel("Configure Profiles")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #F9FAFB;")
        layout.addWidget(title)

        instruction = QLabel("Select profiles for multi-profile processing:")
        instruction.setStyleSheet("color: #9CA3AF;")
        layout.addWidget(instruction)

        self.profile_list = QListWidget()
        self.profile_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        for profile in self.profiles:
            item = QListWidgetItem(f"{profile.name} ({profile.format}, {profile.duration_min:.0f}s-{profile.duration_max:.0f}s)")
            item.setData(Qt.ItemDataRole.UserRole, profile)
            self.profile_list.addItem(item)

        layout.addWidget(self.profile_list)

        return widget

    def _create_export_widget(self):
        widget = QFrame()
        widget.setObjectName("card")
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        title = QLabel("Export Clips")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #F9FAFB;")
        layout.addWidget(title)

        self.export_progress = QProgressBar()
        self.export_progress.setRange(0, 100)
        self.export_progress.setValue(0)
        layout.addWidget(self.export_progress)

        self.export_status = QLabel("Ready to export")
        self.export_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.export_status)

        self.export_log = QTextEdit()
        self.export_log.setReadOnly(True)
        self.export_log.setMaximumHeight(150)
        layout.addWidget(self.export_log)

        return widget

    def _create_button_bar(self):
        bar = QFrame()
        bar.setObjectName("card")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(0, 0, 0, 0)

        self.btn_back = QPushButton("← Back")
        self.btn_back.setEnabled(False)
        self.btn_back.clicked.connect(self._on_back)
        layout.addWidget(self.btn_back)

        layout.addStretch()

        self.btn_next = QPushButton("Next →")
        self.btn_next.clicked.connect(self._on_next)
        layout.addWidget(self.btn_next)

        self.btn_execute = QPushButton("Execute")
        self.btn_execute.setVisible(False)
        self.btn_execute.setProperty("cssClass", "primary")
        self.btn_execute.clicked.connect(self._on_execute)
        layout.addWidget(self.btn_execute)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        layout.addWidget(self.btn_cancel)

        return bar

    def _show_stage(self, stage):
        self.current_stage = stage
        self.upload_widget.setVisible(stage == Stage.UPLOAD)
        self.analyze_widget.setVisible(stage == Stage.ANALYZE)
        self.review_widget.setVisible(stage == Stage.REVIEW)
        self.configure_widget.setVisible(stage == Stage.CONFIGURE)
        self.export_widget.setVisible(stage == Stage.EXPORT)

        for i, (circle, label) in enumerate(self.stage_labels):
            stage_num = i + 1
            is_complete = stage_num < stage.value
            is_current = stage_num == stage.value

            color = "#22C55E" if is_complete else ("#6366F1" if is_current else "#6B7280")
            circle.setStyleSheet(f"color: {color}; font-size: 24px;")
            label.setStyleSheet(f"color: {color}; font-weight: {'bold' if is_current else 'normal'};")

        self.btn_back.setEnabled(stage != Stage.UPLOAD)
        self.btn_next.setVisible(stage not in [Stage.REVIEW, Stage.CONFIGURE, Stage.EXPORT])
        self.btn_execute.setVisible(stage in [Stage.REVIEW, Stage.CONFIGURE])

    def _on_back(self):
        if self.current_stage == Stage.ANALYZE:
            self._show_stage(Stage.UPLOAD)
        elif self.current_stage == Stage.REVIEW:
            self._show_stage(Stage.ANALYZE)
        elif self.current_stage == Stage.CONFIGURE:
            self._show_stage(Stage.REVIEW)
        elif self.current_stage == Stage.EXPORT:
            self._show_stage(Stage.CONFIGURE)

    def _on_next(self):
        if self.current_stage == Stage.UPLOAD:
            self._start_analysis()
        elif self.current_stage == Stage.ANALYZE:
            self._show_stage(Stage.REVIEW)

    def _on_execute(self):
        if self.current_stage == Stage.REVIEW:
            self._start_export()
        elif self.current_stage == Stage.CONFIGURE:
            self._start_export()

    def _start_analysis(self):
        self._show_stage(Stage.ANALYZE)
        self.analyze_progress.setValue(10)
        self.analyze_status.setText("Loading video...")
        self.analyze_substages.setText("Stage: Loading")
        QApplication.processEvents()

        try:
            from core import VideoProcessor, Transcript, Analyzer
            from config.llm_config import LLMConfig

            processor = VideoProcessor()
            self.analyze_progress.setValue(20)
            self.analyze_status.setText("Processing video...")
            self.analyze_substages.setText("Stage: Transcript")
            QApplication.processEvents()

            transcript = Transcript()
            self.analyze_progress.setValue(40)
            self.analyze_status.setText("Extracting highlights...")
            self.analyze_substages.setText("Stage: Candidates")
            QApplication.processEvents()

            provider = "minimax" if LLMConfig.MINIMAX_API_KEY else "mock"
            analyzer = Analyzer(provider=provider)

            if self.profiles:
                profile = self.profiles[0]
            else:
                profile = Profile(name="default", format="16:9", duration_min=60, duration_max=300, quantity=5)

            workflow = VideoClippingWorkflow(self.video_path, profile, analyzer)

            self.analyze_progress.setValue(60)
            self.analyze_substages.setText("Stage: Scoring")
            QApplication.processEvents()

            workflow.execute_stage(WorkflowStage.CANDIDATES_GENERATED)

            self.analyze_progress.setValue(80)
            self.analyze_substages.setText("Stage: Selection")
            QApplication.processEvents()

            workflow.execute_stage(WorkflowStage.SCORED)

            self.scored_highlights = workflow.scored_candidates
            workflow.execute_stage(WorkflowStage.VALIDATED)
            self.highlights = workflow.validated_highlights

            self.analyze_progress.setValue(100)
            self.analyze_status.setText(f"Found {len(self.highlights)} highlights!")
            self.analyze_substages.setText("Stage: Complete")

            self._populate_review_table()

            self._show_stage(Stage.REVIEW)

        except Exception as e:
            logger.error(f"Analysis error: {e}", exc_info=True)
            self.analyze_status.setText(f"Error: {str(e)}")
            self.analyze_status.setStyleSheet("color: #EF4444;")

    def _populate_review_table(self):
        self.highlights_table.setRowCount(0)
        for i, h in enumerate(self.scored_highlights):
            duration = h.get("end", 0) - h.get("start", 0)

            row = self.highlights_table.rowCount()
            self.highlights_table.insertRow(row)

            self.highlights_table.setItem(row, 0, QTableWidgetItem(str(i + 1)))
            self.highlights_table.setItem(row, 1, QTableWidgetItem(f"{h.get('start', 0):.1f}s - {h.get('end', 0):.1f}s"))
            self.highlights_table.setItem(row, 2, QTableWidgetItem(f"{duration:.1f}s"))

            hook_item = QTableWidgetItem(str(h.get("hook_score", 0)))
            hook_item.setBackground(QColor("#22C55E") if h.get("hook_score", 0) > 70 else ("#F59E0B" if h.get("hook_score", 0) > 50 else "#EF4444"))
            self.highlights_table.setItem(row, 3, hook_item)

            viral_item = QTableWidgetItem(str(h.get("viral_score", 0)))
            viral_item.setBackground(QColor("#22C55E") if h.get("viral_score", 0) > 70 else ("#F59E0B" if h.get("viral_score", 0) > 50 else "#EF4444"))
            self.highlights_table.setItem(row, 4, viral_item)

            total_item = QTableWidgetItem(str(h.get("total_score", 0)))
            total_item.setBackground(QColor("#22C55E") if h.get("total_score", 0) > 70 else ("#F59E0B" if h.get("total_score", 0) > 50 else "#EF4444"))
            self.highlights_table.setItem(row, 5, total_item)

            for col in range(6):
                self.highlights_table.item(row, col).setForeground(QColor("#F9FAFB"))

    def _start_export(self):
        self._show_stage(Stage.EXPORT)

        selected_rows = set(item.row() for item in self.highlights_table.selectedItems())
        if not selected_rows:
            selected_rows = set(range(len(self.scored_highlights)))

        selected_highlights = [self.scored_highlights[i] for i in selected_rows]

        selected_profiles = []
        for item in self.profile_list.selectedItems():
            profile = item.data(Qt.ItemDataRole.UserRole)
            if profile:
                selected_profiles.append(profile)

        if not selected_profiles:
            selected_profiles = self.profiles[:1] if self.profiles else [Profile(name="default", format="16:9", duration_min=60, duration_max=300, quantity=5)]

        total_cuts = len(selected_highlights) * len(selected_profiles)
        self.export_progress.setRange(0, total_cuts)
        self.export_progress.setValue(0)

        self.export_log.append(f"Starting export of {len(selected_highlights)} highlights × {len(selected_profiles)} profiles = {total_cuts} clips")

        cut_count = 0
        from core import Cutter

        cutter = Cutter()

        for h in selected_highlights:
            for profile in selected_profiles:
                try:
                    start = h.get("start", 0)
                    end = h.get("end", 0)
                    self.export_log.append(f"Cutting: {start:.1f}s - {end:.1f}s for {profile.name}")

                    output_path = cutter.cut_video(self.video_path, start, end, profile, index=cut_count)
                    self.export_log.append(f"  → Saved: {output_path.name}")

                except Exception as e:
                    self.export_log.append(f"  → Error: {str(e)}")

                cut_count += 1
                self.export_progress.setValue(cut_count)
                QApplication.processEvents()

        self.export_progress.setValue(total_cuts)
        self.export_status.setText(f"Export complete! {total_cuts} clips generated")
        self.export_log.append(f"\n✓ All clips saved to output/")
        self.btn_execute.setVisible(False)
        self.btn_next.setVisible(True)
        self.btn_next.setText("Done")
        self.btn_next.clicked.connect(self.accept)
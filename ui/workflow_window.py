import sys
import logging
from enum import Enum

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QSpinBox,
    QProgressBar, QTextEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QApplication, QSplitter, QStackedWidget,
    QAbstractItemView, QFileDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor

from models.profile import Profile

logger = logging.getLogger(__name__)


class WorkflowWorker(QThread):
    progress = pyqtSignal(int, str, str)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, video_path, profile, analyzer):
        super().__init__()
        self.video_path = video_path
        self.profile = profile
        self.analyzer = analyzer

    def run(self):
        try:
            from core.workflow import VideoClippingWorkflow, WorkflowStage

            workflow = VideoClippingWorkflow(self.video_path, self.profile, self.analyzer)

            self.progress.emit(20, "Loading video...", "Stage: Candidates")
            workflow.execute_stage(WorkflowStage.CANDIDATES_GENERATED)

            self.progress.emit(50, "Scoring candidates...", "Stage: Scoring")
            workflow.execute_stage(WorkflowStage.SCORED)

            self.progress.emit(70, "Selecting highlights...", "Stage: Selection")
            workflow.execute_stage(WorkflowStage.VALIDATED)

            self.progress.emit(100, "Complete!", "Stage: Complete")
            self.finished.emit(workflow.scored_candidates)

        except Exception as e:
            logger.error(f"Workflow error: {e}", exc_info=True)
            self.error.emit(str(e))


STYLESHEET_DARK = """
QMainWindow {
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
QPushButton#startBtn {
    background-color: #6366F1;
    color: white;
    font-weight: bold;
    padding: 12px 24px;
}
QPushButton#startBtn:hover {
    background-color: #818CF8;
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
QLineEdit:disabled {
    background-color: #1F2937;
    color: #6B7280;
}
QSpinBox {
    background-color: #374151;
    color: #F9FAFB;
    border: 1px solid #4B5563;
    border-radius: 4px;
    padding: 4px;
}
QSpinBox:focus {
    border-color: #6366F1;
}
QSpinBox::up-button, QSpinBox::down-button {
    background-color: #4B5563;
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
QTextEdit {
    background-color: #374151;
    color: #F9FAFB;
    border: 1px solid #4B5563;
    border-radius: 4px;
}
"""


class Stage(Enum):
    UPLOAD = 1
    ANALYZE = 2
    REVIEW = 3
    EXPORT = 4


class WorkflowWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scored_highlights = []
        self.current_stage = Stage.UPLOAD
        self._worker = None
        self._setup_ui()
        self.setStyleSheet(STYLESHEET_DARK)
        self.setWindowTitle("CortesVideos - AI Video Clipper")

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setSizes([250, 700])
        splitter.setStretchFactor(1, 1)

        splitter.addWidget(self._create_sidebar())
        splitter.addWidget(self._create_central_area())

        main_layout.addWidget(splitter)

    def _create_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("card")
        sidebar.setFixedWidth(250)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 24, 16, 24)
        layout.setSpacing(16)

        title = QLabel("CONFIG")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #6366F1; letter-spacing: 2px;")
        layout.addWidget(title)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #4B5563;")
        layout.addWidget(line)

        layout.addWidget(QLabel("YouTube URL"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://www.youtube.com/watch?v=...")
        layout.addWidget(self.url_input)

        local_layout = QHBoxLayout()
        local_layout.setSpacing(8)
        btn_browse = QPushButton("Browse...")
        btn_browse.setFixedWidth(80)
        btn_browse.clicked.connect(self._on_browse_video)
        self.local_path_input = QLineEdit()
        self.local_path_input.setPlaceholderText("Or select local file...")
        self.local_path_input.setReadOnly(True)
        local_layout.addWidget(btn_browse)
        local_layout.addWidget(self.local_path_input)
        layout.addLayout(local_layout)

        layout.addSpacing(8)
        layout.addWidget(QLabel("Duration"))
        duration_layout = QHBoxLayout()
        duration_layout.setSpacing(8)

        min_layout = QVBoxLayout()
        min_layout.setSpacing(4)
        min_label = QLabel("Min:")
        min_label.setStyleSheet("color: #9CA3AF; font-size: 12px;")
        self.duration_min_spin = QSpinBox()
        self.duration_min_spin.setRange(10, 3600)
        self.duration_min_spin.setValue(300)
        min_layout.addWidget(min_label)
        min_layout.addWidget(self.duration_min_spin)

        max_layout = QVBoxLayout()
        max_layout.setSpacing(4)
        max_label = QLabel("Max:")
        max_label.setStyleSheet("color: #9CA3AF; font-size: 12px;")
        self.duration_max_spin = QSpinBox()
        self.duration_max_spin.setRange(10, 7200)
        self.duration_max_spin.setValue(900)
        max_layout.addWidget(max_label)
        max_layout.addWidget(self.duration_max_spin)

        duration_layout.addLayout(min_layout)
        duration_layout.addLayout(max_layout)
        layout.addLayout(duration_layout)

        layout.addSpacing(8)
        layout.addWidget(QLabel("Quantity"))
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 20)
        self.quantity_spin.setValue(5)
        layout.addWidget(self.quantity_spin)

        layout.addSpacing(8)
        layout.addWidget(QLabel("Score Minimum"))
        self.score_min_spin = QSpinBox()
        self.score_min_spin.setRange(0, 100)
        self.score_min_spin.setValue(60)
        layout.addWidget(self.score_min_spin)

        layout.addStretch()

        self.start_btn = QPushButton("START WORKFLOW")
        self.start_btn.setObjectName("startBtn")
        self.start_btn.clicked.connect(self._on_start_workflow)
        layout.addWidget(self.start_btn)

        return sidebar

    def _create_central_area(self):
        central = QFrame()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        layout.addWidget(self._create_stage_indicator())
        layout.addWidget(self._create_content_stack())

        return central

    def _create_stage_indicator(self):
        container = QFrame()
        container.setObjectName("card")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(24, 16, 24, 16)

        self.stage_widgets = []
        stages = ["Upload", "Analyze", "Review", "Export"]

        for i, name in enumerate(stages, 1):
            stage_layout = QVBoxLayout()
            stage_layout.setSpacing(4)
            stage_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            circle = QLabel("○")
            circle.setAlignment(Qt.AlignmentFlag.AlignCenter)
            circle.setStyleSheet("color: #6B7280; font-size: 24px;")
            circle.setProperty("stage", i)

            label = QLabel(name)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("color: #6B7280; font-size: 12px;")
            label.setProperty("stage", i)

            self.stage_widgets.append((circle, label))
            stage_layout.addWidget(circle)
            stage_layout.addWidget(label)
            layout.addLayout(stage_layout)

            if i < 4:
                line = QLabel("→")
                line.setStyleSheet("color: #4B5563; font-size: 20px;")
                layout.addWidget(line)

        return container

    def _create_content_stack(self):
        self.content_stack = QStackedWidget()

        self.upload_widget = self._create_upload_content()
        self.analyze_widget = self._create_analyze_content()
        self.review_widget = self._create_review_content()
        self.export_widget = self._create_export_content()

        self.content_stack.addWidget(self.upload_widget)
        self.content_stack.addWidget(self.analyze_widget)
        self.content_stack.addWidget(self.review_widget)
        self.content_stack.addWidget(self.export_widget)

        return self.content_stack

    def _create_upload_content(self):
        widget = QFrame()
        widget.setObjectName("card")
        layout = QVBoxLayout(widget)
        layout.setSpacing(16)

        self.upload_title = QLabel("Video Ready")
        self.upload_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #F9FAFB;")
        layout.addWidget(self.upload_title)

        self.upload_url_label = QLabel("YouTube URL: (enter in sidebar)")
        self.upload_url_label.setStyleSheet("color: #9CA3AF; font-size: 12px;")
        self.upload_url_label.setWordWrap(True)
        layout.addWidget(self.upload_url_label)

        self.upload_status_label = QLabel("Waiting for workflow start...")
        self.upload_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.upload_status_label.setStyleSheet("color: #6B7280; font-size: 14px;")
        layout.addWidget(self.upload_status_label)

        layout.addStretch()
        return widget

    def _create_analyze_content(self):
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

    def _create_review_content(self):
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

        info = QLabel("Highlights to export")
        info.setStyleSheet("color: #9CA3AF; font-size: 12px;")
        layout.addWidget(info)

        self.btn_export = QPushButton("EXPORT CLIPS")
        self.btn_export.setObjectName("startBtn")
        self.btn_export.clicked.connect(self._on_export_clips)
        layout.addWidget(self.btn_export)

        return widget

    def _create_export_content(self):
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

        layout.addStretch()
        return widget

    def _show_stage(self, stage):
        self.current_stage = stage
        self.content_stack.setCurrentIndex(stage.value - 1)

        for i, (circle, label) in enumerate(self.stage_widgets):
            stage_num = i + 1
            is_complete = stage_num < stage.value
            is_current = stage_num == stage.value

            if is_complete:
                color = "#22C55E"
                circle.setText("●")
            elif is_current:
                color = "#6366F1"
                circle.setText("●")
            else:
                color = "#6B7280"
                circle.setText("○")

            circle.setStyleSheet(f"color: {color}; font-size: 24px;")
            label.setStyleSheet(f"color: {color}; font-weight: {'bold' if is_current else 'normal'};")

    def _on_browse_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            "",
            "Video Files (*.mp4 *.mkv *.avi *.mov *.webm);;All Files (*)"
        )
        if file_path:
            self.local_path_input.setText(file_path)
            self.url_input.setText("")  # Clear URL when local file selected

    def _on_start_workflow(self):
        url = self.url_input.text().strip()
        local_path = self.local_path_input.text().strip()

        if not url and not local_path:
            self.url_input.setStyleSheet(STYLESHEET_DARK + "QLineEdit { border: 2px solid #EF4444; }")
            return

        self.url_input.setStyleSheet(STYLESHEET_DARK)

        self.video_path = local_path if local_path else url
        display_path = local_path if local_path else url

        self.upload_url_label.setText(f"Video: {display_path}")
        self.upload_status_label.setText("Processing video...")
        self.upload_title.setText("Video Loaded")

        duration_min = self.duration_min_spin.value()
        duration_max = self.duration_max_spin.value()
        quantity = self.quantity_spin.value()
        score_minimum = self.score_min_spin.value()

        profile = Profile(
            name="default",
            format="16:9",
            duration_min=float(duration_min),
            duration_max=float(duration_max),
            quantity=quantity,
            score_minimum=score_minimum
        )

        from core import Analyzer
        from config.llm_config import LLMConfig

        provider = "minimax" if LLMConfig.MINIMAX_API_KEY else "mock"
        analyzer = Analyzer(provider=provider)

        self._show_stage(Stage.ANALYZE)
        self.analyze_progress.setValue(5)
        self.analyze_status.setText("Initializing workflow...")
        self.analyze_substages.setText("Stage: Loading")
        QApplication.processEvents()

        self._worker = WorkflowWorker(self.video_path, profile, analyzer)
        self._worker.progress.connect(self._on_worker_progress)
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.error.connect(self._on_worker_error)
        self._worker.start()

    def _on_worker_progress(self, value, status, substage):
        self.analyze_progress.setValue(value)
        self.analyze_status.setText(status)
        self.analyze_substages.setText(substage)

        if value >= 20:
            self._update_stage_indicator(1)
        if value >= 50:
            self._update_stage_indicator(2)
        if value >= 70:
            self._update_stage_indicator(3)

    def _update_stage_indicator(self, stage_num):
        for i, (circle, label) in enumerate(self.stage_widgets):
            if i + 1 <= stage_num:
                color = "#22C55E"
                circle.setText("●")
            elif i + 1 == stage_num + 1:
                color = "#6366F1"
                circle.setText("●")
            else:
                color = "#6B7280"
                circle.setText("○")
            circle.setStyleSheet(f"color: {color}; font-size: 24px;")

    def _on_worker_finished(self, scored_highlights):
        self.scored_highlights = scored_highlights
        self._populate_review_table()
        self._show_stage(Stage.REVIEW)
        self._update_stage_indicator(4)

    def _on_worker_error(self, error_msg):
        logger.error(f"Analysis error: {error_msg}")
        self.analyze_status.setText(f"Error: {error_msg}")
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
            hook_item.setBackground(QColor("#22C55E") if h.get("hook_score", 0) > 70 else (QColor("#F59E0B") if h.get("hook_score", 0) > 50 else QColor("#EF4444")))
            self.highlights_table.setItem(row, 3, hook_item)

            viral_item = QTableWidgetItem(str(h.get("viral_score", 0)))
            viral_item.setBackground(QColor("#22C55E") if h.get("viral_score", 0) > 70 else (QColor("#F59E0B") if h.get("viral_score", 0) > 50 else QColor("#EF4444")))
            self.highlights_table.setItem(row, 4, viral_item)

            total_item = QTableWidgetItem(str(h.get("total_score", 0)))
            total_item.setBackground(QColor("#22C55E") if h.get("total_score", 0) > 70 else (QColor("#F59E0B") if h.get("total_score", 0) > 50 else QColor("#EF4444")))
            self.highlights_table.setItem(row, 5, total_item)

            for col in range(6):
                self.highlights_table.item(row, col).setForeground(QColor("#F9FAFB"))

    def _on_export_clips(self):
        self._show_stage(Stage.EXPORT)
        self._update_stage_indicator(4)

        selected_rows = set(item.row() for item in self.highlights_table.selectedItems())
        if not selected_rows:
            selected_rows = set(range(len(self.scored_highlights)))

        selected_highlights = [self.scored_highlights[i] for i in selected_rows]

        total_cuts = len(selected_highlights)
        self.export_progress.setRange(0, total_cuts)
        self.export_progress.setValue(0)

        self.export_log.append(f"Starting export of {len(selected_highlights)} clips")

        cut_count = 0
        from core import Cutter

        cutter = Cutter()

        for h in selected_highlights:
            try:
                start = h.get("start", 0)
                end = h.get("end", 0)
                self.export_log.append(f"Cutting: {start:.1f}s - {end:.1f}s")

                profile = Profile(
                    name="default",
                    format="16:9",
                    duration_min=float(self.duration_min_spin.value()),
                    duration_max=float(self.duration_max_spin.value()),
                    quantity=1,
                    score_minimum=0
                )

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
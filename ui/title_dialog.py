# ui/title_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QRadioButton,
    QCheckBox, QTextEdit, QLabel, QPushButton, QWidget,
    QStackedWidget, QScrollArea, QButtonGroup
)
from PyQt6.QtCore import Qt

from core.title_generator import TEMPLATES

class TitleConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurar Geração de Títulos")
        self.setMinimumSize(500, 400)

        self.mode = "auto"
        self.config = {}

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Step indicator
        self.step_label = QLabel("<b>Step 1: Escolha o Modo</b>")
        layout.addWidget(self.step_label)

        # Mode selection
        self.mode_group = QWidget()
        mode_layout = QVBoxLayout(self.mode_group)

        self.radio_auto = QRadioButton("Auto - IA decide o melhor título")
        self.radio_auto.setChecked(True)
        self.radio_auto.toggled.connect(lambda checked: self._show_config("auto") if checked else None)
        mode_layout.addWidget(self.radio_auto)

        self.radio_template = QRadioButton("Template - Escolher templates pré-definidos")
        self.radio_template.toggled.connect(lambda checked: self._show_config("template") if checked else None)
        mode_layout.addWidget(self.radio_template)

        self.radio_custom = QRadioButton("Custom - Escrever prompt personalizado")
        self.radio_custom.toggled.connect(lambda checked: self._show_config("custom") if checked else None)
        mode_layout.addWidget(self.radio_custom)

        layout.addWidget(self.mode_group)

        # Config area
        self.config_stack = QStackedWidget()
        layout.addWidget(self.config_stack)

        # Auto config
        auto_widget = QWidget()
        auto_layout = QVBoxLayout(auto_widget)
        auto_layout.addWidget(QLabel("Título será gerado automaticamente baseado no conteúdo do highlight."))
        self.config_stack.addWidget(auto_widget)

        # Template config
        template_widget = QScrollArea()
        template_widget.setWidgetResizable(True)
        template_content = QWidget()
        template_layout = QVBoxLayout(template_content)

        self.template_checks = {}
        for category, templates_list in TEMPLATES.items():
            cat_widget = QWidget()
            cat_layout = QVBoxLayout(cat_widget)
            cat_layout.addWidget(QLabel(f"<b>{category.capitalize()}</b>"))
            for t in templates_list:
                cb = QCheckBox(t)
                if category not in self.template_checks:
                    self.template_checks[category] = []
                self.template_checks[category].append(cb)
                cat_layout.addWidget(cb)
            template_layout.addWidget(cat_widget)
        template_widget.setWidget(template_content)
        self.config_stack.addWidget(template_widget)

        # Custom config
        custom_widget = QWidget()
        custom_layout = QVBoxLayout(custom_widget)
        custom_layout.addWidget(QLabel("Prompt personalizado:"))
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("Escreva seu prompt... Use {text}, {start}, {end}, {duration}")
        custom_layout.addWidget(self.prompt_edit)
        custom_layout.addWidget(QLabel("<i>Variáveis disponíveis: {text}, {start}, {end}, {duration}</i>"))
        self.config_stack.addWidget(custom_widget)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_process = QPushButton("Processar")
        self.btn_process.clicked.connect(self._collect_and_accept)
        btn_layout.addWidget(self.btn_process)

        layout.addLayout(btn_layout)

        self._show_config("auto")

    def _show_config(self, mode):
        self.mode = mode
        if mode == "auto":
            self.config_stack.setCurrentIndex(0)
        elif mode == "template":
            self.config_stack.setCurrentIndex(1)
        elif mode == "custom":
            self.config_stack.setCurrentIndex(2)

    def _collect_and_accept(self):
        self.config = {"mode": self.mode}
        if self.mode == "template":
            selected = []
            for cat, checks in self.template_checks.items():
                for cb in checks:
                    if cb.isChecked():
                        selected.append(cat)
                        break
            self.config["templates"] = selected
        elif self.mode == "custom":
            self.config["prompt"] = self.prompt_edit.toPlainText()
        self.accept()

    def get_config(self):
        return self.mode, self.config
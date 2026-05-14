from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QComboBox,
    QSpinBox, QDoubleSpinBox, QCheckBox, QPushButton,
    QFormLayout
)

class ProfileDialog(QDialog):
    def __init__(self, profile=None):
        super().__init__()
        self.setWindowTitle("Perfil de Corte")
        self.profile = profile

        layout = QVBoxLayout(self)

        form = QFormLayout()

        self.name = QLineEdit()
        form.addRow("Nome:", self.name)

        self.format = QComboBox()
        self.format.addItems(["9:16", "1:1", "16:9", "4:3"])
        form.addRow("Formato:", self.format)

        self.duration_min = QDoubleSpinBox()
        self.duration_min.setRange(5, 300)
        self.duration_min.setValue(15)
        form.addRow("Duração Mín (s):", self.duration_min)

        self.duration_max = QDoubleSpinBox()
        self.duration_max.setRange(10, 600)
        self.duration_max.setValue(60)
        form.addRow("Duração Máx (s):", self.duration_max)

        self.quantity = QSpinBox()
        self.quantity.setRange(1, 50)
        self.quantity.setValue(5)
        form.addRow("Quantidade:", self.quantity)

        self.score_minimum = QSpinBox()
        self.score_minimum.setRange(0, 100)
        self.score_minimum.setValue(60)
        form.addRow("Score Mínimo:", self.score_minimum)

        self.tipo = QComboBox()
        self.tipo.addItems(["short", "medio", "normal"])
        form.addRow("Tipo:", self.tipo)

        self.face_crop = QCheckBox()
        form.addRow("Crop Rosto:", self.face_crop)

        layout.addLayout(form)

        buttons = QPushButton("Salvar")
        buttons.clicked.connect(self.accept)
        layout.addWidget(buttons)

        if profile:
            self._load_profile(profile)

    def _load_profile(self, profile):
        self.name.setText(profile.name)
        self.format.setCurrentText(profile.format)
        self.duration_min.setValue(profile.duration_min)
        self.duration_max.setValue(profile.duration_max)
        self.quantity.setValue(profile.quantity)
        self.score_minimum.setValue(profile.score_minimum)
        self.tipo.setCurrentText(profile.tipo)
        self.face_crop.setChecked(profile.face_crop)

    def get_profile(self):
        from models.profile import Profile
        return Profile(
            name=self.name.text(),
            format=self.format.currentText(),
            duration_min=self.duration_min.value(),
            duration_max=self.duration_max.value(),
            quantity=self.quantity.value(),
            score_minimum=self.score_minimum.value(),
            tipo=self.tipo.currentText(),
            face_crop=self.face_crop.isChecked()
        )
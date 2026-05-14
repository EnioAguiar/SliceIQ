# ui/toast.py
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer, Qt

class ToastNotification(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        self.label = QLabel()
        self.label.setStyleSheet("""
            background-color: #2d2d2d;
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            font-size: 14px;
        """)
        layout.addWidget(self.label)

        self.timer = QTimer()
        self.timer.timeout.connect(self._fade_out)

    def show_message(self, text: str, duration: int = 3000):
        self.label.setText(text)
        self.adjustSize()

        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        self.move(
            screen.width() // 2 - self.width() // 2,
            screen.height() - 100
        )

        self.show()
        self.timer.start(duration)

    def _fade_out(self):
        self.timer.stop()
        self.close()
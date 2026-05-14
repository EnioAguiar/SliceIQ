import sys
import os
os.environ['LANG'] = 'en_US.UTF-8'
os.environ['LC_ALL'] = 'en_US.UTF-8'
os.environ['PYTHONUTF8'] = '1'

from dotenv import load_dotenv
load_dotenv()

from PyQt6.QtWidgets import QApplication
from ui.workflow_window import WorkflowWindow

def main():
    app = QApplication(sys.argv)
    window = WorkflowWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
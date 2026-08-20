import os
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from app.app_window import MainWindow, apply_style

if __name__ == "__main__":
    print("Starting application...")
    os.makedirs("app\\Temp", exist_ok=True)
    app = QApplication(sys.argv)

    # icon, styles, window setup

    app.setWindowIcon(QIcon("icon.ico"))

    apply_style(app)

    window = MainWindow()
    window.setWindowTitle("Image Translation Tool")
    window.show()

    sys.exit(app.exec())

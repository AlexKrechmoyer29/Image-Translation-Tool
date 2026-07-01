import sys
from PySide6.QtWidgets import QApplication
from app.app_window import MainWindow, apply_style

if __name__ == "__main__":
    # Entry point for application and start up PySide6 QApp
    print("Starting application...")
    app = QApplication(sys.argv)
    apply_style(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

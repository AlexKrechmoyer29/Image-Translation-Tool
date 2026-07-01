import sys
from PySide6.QtWidgets import QApplication, QStyleFactory
from app.overlay import SnipOverlay
from app.translate import initTranslationPkg, translateText
from app.app_window import MainWindow, apply_style

if __name__ == "__main__":
    # Entry point for application and start up PySide6 QApp
    print("Starting application...")
    app = QApplication(sys.argv)
    apply_style(app)
    app.setStyle(QStyleFactory.create("Fusion"))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
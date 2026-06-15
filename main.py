import sys
from PySide6.QtWidgets import QApplication
from app.overlay import SnipOverlay

# Entry point for application and start up PySide6 QApp
app = QApplication(sys.argv)

# Create snipping overlay (transparent, top of screen order)
overlay = SnipOverlay()
overlay.showFullScreen()

sys.exit(app.exec())

# Receives screeshot region

# Send image to OCR

# Send image to translation

# Open result window or print
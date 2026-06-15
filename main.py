import sys
from PySide6.QtWidgets import QApplication
from app.overlay import SnipOverlay
from app.translate import initTranslationPkg, translateText

# Entry point for application and start up PySide6 QApp
app = QApplication(sys.argv)

# Create snipping overlay (transparent, top of screen order)
overlay = SnipOverlay()
overlay.showFullScreen()

fromLang = "en"
toLang = "es"
# Begin event tracking
try:
    app.exec()
    print("Done")
finally:
    # Call OCR and translation tools
    print("TRYING")
    print(initTranslationPkg(fromLang, toLang))
    print("Translate")
    translateText()

sys.exit()



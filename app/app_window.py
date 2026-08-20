from PySide6.QtWidgets import (
    QMainWindow, QWidget, QFrame, QLabel, QStackedWidget, QStyleFactory, 
    QHBoxLayout, QVBoxLayout, QGridLayout, QSizePolicy, QPushButton, QApplication,
    QComboBox, QRadioButton, QButtonGroup, QGroupBox, QPlainTextEdit, QCheckBox
)
from PySide6.QtGui import QPalette, QColor, QPixmap
from PySide6.QtCore import Qt, QTimer, QSettings, QObject, Signal, QThread
from app.overlay import SnipOverlay
import sys


def _translate_module(preload_model=None, unload_after_use=None):
    import importlib

    module = importlib.import_module("app.translate")
    if preload_model is not None:
        module.preload_model = preload_model
    if unload_after_use is not None:
        module.unload_after_use = unload_after_use
    return module


class TranslationWarmupWorker(QObject):
    finished = Signal()
    failed = Signal(str)

    def __init__(self, from_lang, to_lang, preload_model, unload_after_use):
        super().__init__()
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.preload_model = preload_model
        self.unload_after_use = unload_after_use

    def run(self):
        try:
            translate = _translate_module(self.preload_model, self.unload_after_use)
            translate.preloadTranslationPkg(self.from_lang, self.to_lang)
        except Exception as exc:
            self.failed.emit(str(exc))
        else:
            self.finished.emit()


class TranslationWorker(QObject):
    finished = Signal(str)
    failed = Signal(str)

    def __init__(self, from_lang, to_lang, preload_model, unload_after_use):
        super().__init__()
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.preload_model = preload_model
        self.unload_after_use = unload_after_use

    def run(self):
        try:
            translate = _translate_module(self.preload_model, self.unload_after_use)
            translate.initTranslationPkg(self.from_lang, self.to_lang)
            result = translate.translateText()
        except Exception as exc:
            self.failed.emit(str(exc))
        else:
            self.finished.emit(result)

def apply_style(app: QApplication) -> None:
    app.setStyle(QStyleFactory.create("Fusion"))

    # Font size 
    default_font = QApplication.font()
    default_font.setPointSize(default_font.pointSize() + 2)
    app.setFont(default_font)

    # Palette
    dark_palette = QPalette()

    ColorRole = QPalette.ColorRole
    ColorGroup = QPalette.ColorGroup

    dark_palette.setColor(ColorRole.Window, QColor(53, 53, 53))
    dark_palette.setColor(ColorRole.WindowText, Qt.GlobalColor.white)
    dark_palette.setColor(ColorGroup.Disabled, ColorRole.WindowText, QColor(127, 127, 127))

    dark_palette.setColor(ColorRole.Base, QColor(42, 42, 42))
    dark_palette.setColor(ColorRole.AlternateBase, QColor(66, 66, 66))

    dark_palette.setColor(ColorRole.ToolTipBase, Qt.GlobalColor.white)
    dark_palette.setColor(ColorRole.ToolTipText, Qt.GlobalColor.white)

    dark_palette.setColor(ColorRole.Text, Qt.GlobalColor.white)
    dark_palette.setColor(ColorGroup.Disabled, ColorRole.Text, QColor(127, 127, 127))

    dark_palette.setColor(ColorRole.Dark, QColor(35, 35, 35))
    dark_palette.setColor(ColorRole.Shadow, QColor(20, 20, 20))

    dark_palette.setColor(ColorRole.Button, QColor(53, 53, 53))
    dark_palette.setColor(ColorRole.ButtonText, Qt.GlobalColor.white)
    dark_palette.setColor(ColorGroup.Disabled, ColorRole.ButtonText, QColor(127, 127, 127))

    dark_palette.setColor(ColorRole.BrightText, Qt.GlobalColor.red)
    dark_palette.setColor(ColorRole.Link, QColor(42, 130, 218))

    dark_palette.setColor(ColorRole.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(ColorGroup.Disabled, ColorRole.Highlight, QColor(80, 80, 80))

    dark_palette.setColor(ColorRole.HighlightedText, Qt.GlobalColor.white)
    dark_palette.setColor(ColorGroup.Disabled, ColorRole.HighlightedText, QColor(127, 127, 127))

    app.setPalette(dark_palette)

class MainWindow(QMainWindow):
    LANG_CODES = {
        "Albanian": "sq",
        "Arabic": "ar",
        "Azerbaijani": "az",
        "Basque": "eu",
        "Bengali": "bn",
        "Bulgarian": "bg",
        "Catalan": "ca",
        "Chinese": "zh",
        "Chinese Traditional": "zt",
        "Czech": "cs",
        "Danish": "da",
        "Dutch": "nl",
        "English": "en",
        "Esperanto": "eo",
        "Estonian": "et",
        "Finnish": "fi",
        "French": "fr",
        "Galician": "gl",
        "German": "de",
        "Greek": "el",
        "Hebrew": "he",
        "Hindi": "hi",
        "Hungarian": "hu",
        "Indonesian": "id",
        "Irish": "ga",
        "Italian": "it",
        "Japanese": "ja",
        "Korean": "ko",
        "Kyrgyz": "ky",
        "Latvian": "lv",
        "Lithuanian": "lt",
        "Malay": "ms",
        "Norwegian Bokmal": "nb",
        "Persian": "fa",
        "Polish": "pl",
        "Portuguese": "pt",
        "Portuguese Brazil": "pb",
        "Romanian": "ro",
        "Russian": "ru",
        "Serbian": "sr",
        "Slovak": "sk",
        "Slovenian": "sl",
        "Spanish": "es",
        "Swedish": "sv",
        "Tagalog": "tl",
        "Thai": "th",
        "Turkish": "tr",
        "Ukrainian": "uk",
        "Urdu": "ur",
        "Vietnamese": "vi",
    } 
    
    def __init__(self, parent=None):  
        super().__init__()
        self._warmup_thread = None
        self._warmup_worker = None
        self._translation_thread = None
        self._translation_worker = None
        
        # Top Bar

        topBar = QFrame()
        topLogo = QLabel()
        topLogo.setPixmap(QPixmap("banner.png"))
        topLogo.setScaledContents(True)
        topLogo.setFixedWidth(400)
        topLogo.setFixedHeight(100)

        menuBar = QFrame()

        # Language Settings

        self.menuLang = QLabel("Language")

        self.menuFromLang = QComboBox()
        self.menuToLang = QComboBox()

        self.menuFromLang.addItems(list(self.LANG_CODES.keys()))
        self.menuToLang.addItems(["English"])


        # Handler for updating "To" language options based on selected "From" language and vice versa.

        def updateToLang(index):
            selected = self.menuFromLang.currentText()

            self.menuToLang.blockSignals(True)
            self.menuToLang.clear()

            if selected == "English":
                self.menuToLang.addItems(list(self.LANG_CODES.keys()))
            else:
                self.menuToLang.addItems(["English"])

            self.menuToLang.blockSignals(False)


        def updateFromLang(index):
            selected = self.menuToLang.currentText()

            self.menuFromLang.blockSignals(True)
            self.menuFromLang.clear()

            if selected == "English":
                self.menuFromLang.addItems(list(self.LANG_CODES.keys()))
            else:
                self.menuFromLang.addItems(["English"])

            self.menuFromLang.blockSignals(False)


        self.menuFromLang.currentIndexChanged.connect(updateToLang)
        self.menuToLang.currentIndexChanged.connect(updateFromLang)
        self.menuFromLang.currentIndexChanged.connect(self.saveLanguageSettings)
        self.menuToLang.currentIndexChanged.connect(self.saveLanguageSettings)

        updateToLang(0)

        # AI Settings

        menuAI = QLabel("AI")
        menuAIYes = QRadioButton("Yes")
        menuAINo = QRadioButton("No")

        group = QButtonGroup(self)
        group.addButton(menuAIYes)
        group.addButton(menuAINo)
        menuAINo.setChecked(True)
        # readYesNo = group.checkedButton().text()

        # Model Settings

        self.preloadCheck = QCheckBox("Pre-load Models")
        self.unloadCheck = QCheckBox("Unload After Each Use")

        # Window Pinning
        
        self.pinCheck = QCheckBox("Pin Window")
        self.pinCheck.toggled.connect(self.pinToggled)
        self.loadLanguageSettings()

        self.preloadCheck.stateChanged.connect(self.onPreloadChanged)
        self.unloadCheck.stateChanged.connect(self.onUnloadChanged)
        self.preloadCheck.stateChanged.connect(self.saveLanguageSettings)
        self.unloadCheck.stateChanged.connect(self.saveLanguageSettings)

        # Image Selection Button

        capImageButton = QPushButton("Capture Image")
        capImageButton.clicked.connect(lambda: self.showOverlay())

        # Output

        outputBox = QGroupBox("Output")
        self.outputDisplay = QPlainTextEdit()

        central_widget = QWidget()

        # Layouts

        topBarLayout = QHBoxLayout()
        menuBarLayout = QGridLayout()
        outputLayout = QVBoxLayout()
        centralLayout = QVBoxLayout()

        # Top Bar Layout

        topBarLayout.addWidget(topLogo)
        topBar.setLayout(topBarLayout)
        topBar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Menu Bar Layout

        menuBarLayout.addWidget(self.menuLang, 0, 0)
        menuBarLayout.addWidget(self.menuFromLang, 0, 1)
        menuBarLayout.addWidget(self.menuToLang, 0, 2)

        menuBarLayout.addWidget(menuAI, 1, 0)
        menuBarLayout.addWidget(menuAIYes, 1, 1)
        menuBarLayout.addWidget(menuAINo, 1, 2)

        menuBarLayout.addWidget(self.preloadCheck, 2, 0, 1, 2)
        menuBarLayout.addWidget(self.unloadCheck, 2, 2)

        menuBarLayout.addWidget(capImageButton, 3, 0, 1, 3)

        menuBar.setLayout(menuBarLayout)
        menuBar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Output Layout

        self.outputDisplay.setReadOnly(True)
        self.outputDisplay.appendPlainText("Translation will appear here...")
        outputLayout.addWidget(self.outputDisplay)
        outputBox.setLayout(outputLayout)
        outputBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
        # Central Layout

        centralLayout.addWidget(topBar)
        centralLayout.addWidget(menuBar)
        centralLayout.addWidget(outputBox, 1)
        centralLayout.addWidget(self.pinCheck, Qt.AlignRight)

        central_widget.setLayout(centralLayout)
        self.setCentralWidget(central_widget)

        
        # Model Preloading and Settings Functions

        if self.preloadCheck.isChecked():
            QTimer.singleShot(0, self.preloadAtStartup)

    # Handler for window pinning

    def pinToggled(self, checked):
            self.setWindowFlag(Qt.WindowStaysOnTopHint, checked)
            self.show() 
            self.saveLanguageSettings()

    def loadLanguageSettings(self):
        settings = QSettings("ITT", "ImageTranslationTool")
        from_lang = settings.value("from_lang", "Spanish")
        to_lang = settings.value("to_lang", "English")
        self.preloadCheck.setChecked(settings.value("preload", True, type=bool))
        self.unloadCheck.setChecked(settings.value("unload", False, type=bool))
        # Restore from_lang first so updateToLang populates menuToLang,
        # then restore from_lang so it sticks as the final selection.
        from_idx = self.menuFromLang.findText(from_lang)
        if from_idx >= 0:
            self.menuFromLang.setCurrentIndex(from_idx)
        to_idx = self.menuToLang.findText(to_lang)
        if to_idx >= 0:
            self.menuToLang.setCurrentIndex(to_idx)
        self.pinCheck.setChecked(settings.value("pin_window", False, type=bool))

    def saveLanguageSettings(self):
        settings = QSettings("ITT", "ImageTranslationTool")
        settings.setValue("from_lang", self.menuFromLang.currentText())
        settings.setValue("to_lang", self.menuToLang.currentText())
        settings.setValue("preload", self.preloadCheck.isChecked())
        settings.setValue("unload", self.unloadCheck.isChecked())
        settings.setValue("pin_window", self.pinCheck.isChecked())
        settings.sync()

    def _updateLoadedTranslateSettings(self):
        module = sys.modules.get("app.translate")
        if module is not None:
            module.preload_model = self.preloadCheck.isChecked()
            module.unload_after_use = self.unloadCheck.isChecked()

    def onPreloadChanged(self, state):
        self._updateLoadedTranslateSettings()

    def onUnloadChanged(self, state):
        self._updateLoadedTranslateSettings()

    def preloadAtStartup(self):
        if self._warmup_thread is not None:
            return

        fromLang = self.LANG_CODES[self.menuFromLang.currentText()]
        toLang = self.LANG_CODES[self.menuToLang.currentText()]
        self._warmup_thread = QThread(self)
        self._warmup_worker = TranslationWarmupWorker(
            fromLang,
            toLang,
            self.preloadCheck.isChecked(),
            self.unloadCheck.isChecked(),
        )
        self._warmup_worker.moveToThread(self._warmup_thread)
        self._warmup_thread.started.connect(self._warmup_worker.run)
        self._warmup_worker.finished.connect(self._warmup_thread.quit)
        self._warmup_worker.failed.connect(self._warmup_thread.quit)
        self._warmup_worker.finished.connect(self._warmup_worker.deleteLater)
        self._warmup_worker.failed.connect(self._warmup_worker.deleteLater)
        self._warmup_thread.finished.connect(self._warmup_thread.deleteLater)
        self._warmup_thread.finished.connect(lambda: setattr(self, "_warmup_thread", None))
        self._warmup_thread.finished.connect(lambda: setattr(self, "_warmup_worker", None))
        self._warmup_worker.failed.connect(lambda message: print(f"Warmup failed: {message}"))
        self._warmup_thread.start()

    def translateImage(self, fromLang, toLang):
        self.show()
        self.raise_()
        self.activateWindow()

        if self._translation_thread is not None:
            return

        self.outputDisplay.setPlainText("Processing screenshot...")

        self._translation_thread = QThread(self)
        self._translation_worker = TranslationWorker(
            fromLang,
            toLang,
            self.preloadCheck.isChecked(),
            self.unloadCheck.isChecked(),
        )
        self._translation_worker.moveToThread(self._translation_thread)
        self._translation_thread.started.connect(self._translation_worker.run)
        self._translation_worker.finished.connect(self.outputDisplay.setPlainText)
        self._translation_worker.finished.connect(self._translation_thread.quit)
        self._translation_worker.failed.connect(
            lambda message: self.outputDisplay.setPlainText(f"Translation failed:\n{message}")
        )
        self._translation_worker.failed.connect(self._translation_thread.quit)
        self._translation_worker.finished.connect(self._translation_worker.deleteLater)
        self._translation_worker.failed.connect(self._translation_worker.deleteLater)
        self._translation_thread.finished.connect(self._translation_thread.deleteLater)
        self._translation_thread.finished.connect(lambda: setattr(self, "_translation_thread", None))
        self._translation_thread.finished.connect(lambda: setattr(self, "_translation_worker", None))
        self._translation_thread.start()

    def showOverlay(self):
        self.hide()
        self.overlay = SnipOverlay()
        self.overlay.destroyed.connect(self._restoreWindowAfterOverlay)

        fromLang = self.LANG_CODES[self.menuFromLang.currentText()]
        toLang = self.LANG_CODES[self.menuToLang.currentText()]

        self.overlay.captureComplete.connect(lambda: self.translateImage(fromLang, toLang))

        self.overlay.showFullScreen()

    def _restoreWindowAfterOverlay(self):
        if self._translation_thread is None:
            self.show()
            self.raise_()
            self.activateWindow()

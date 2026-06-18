from PySide6.QtWidgets import (
    QMainWindow, QWidget, QFrame, QLabel, QStackedWidget, QStyleFactory, 
    QHBoxLayout, QVBoxLayout, QGridLayout, QSizePolicy, QPushButton, QApplication,
    QComboBox, QRadioButton, QButtonGroup, QGroupBox, QPlainTextEdit, QCheckBox
)
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt, QTimer, QSettings
from app.overlay import SnipOverlay
import app.translate

def apply_dark_fusion_style(app: QApplication) -> None:
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
        
        # Top Bar

        topBar = QFrame()
        topLogo = QLabel("Logo")
        title = QLabel("Title")

        menuBar = QFrame()

        # Language Settings

        self.menuLang = QLabel("Language")

        self.menuFromLang = QComboBox()
        self.menuToLang = QComboBox()

        self.menuFromLang.addItems(["Spanish", "German", "English"])
        self.menuToLang.addItems(["English"])

        def updateToLang(index):
            selected = self.menuFromLang.currentText()

            self.menuToLang.blockSignals(True)
            self.menuToLang.clear()

            if selected == "English":
                self.menuToLang.addItems(["Spanish", "German", "English"])
            else:
                self.menuToLang.addItems(["English"])

            self.menuToLang.blockSignals(False)


        def updateFromLang(index):
            selected = self.menuToLang.currentText()

            self.menuFromLang.blockSignals(True)
            self.menuFromLang.clear()

            if selected == "English":
                self.menuFromLang.addItems(["Spanish", "German", "English"])
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
        self.preloadCheck.setChecked(app.translate.preload_model)
        self.unloadCheck = QCheckBox("Unload After Each Use")
        self.unloadCheck.setChecked(app.translate.unload_after_use)

        self.preloadCheck.stateChanged.connect(self.onPreloadChanged)
        self.unloadCheck.stateChanged.connect(self.onUnloadChanged)
        self.preloadCheck.stateChanged.connect(self.saveLanguageSettings)
        self.unloadCheck.stateChanged.connect(self.saveLanguageSettings)

        self.loadLanguageSettings()

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

        topBarLayout.addWidget(topLogo, 1, Qt.AlignLeft)
        topBarLayout.addWidget(title, 3, Qt.AlignCenter)
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

        central_widget.setLayout(centralLayout)
        self.setCentralWidget(central_widget)

        
        # Model Preloading and Settings Functions

        if app.translate.preload_model:
            QTimer.singleShot(0, self.preloadAtStartup)

    def loadLanguageSettings(self):
        settings = QSettings("ITT", "ImageTranslationTool")
        from_lang = settings.value("from_lang", "Spanish")
        to_lang = settings.value("to_lang", "English")
        import app.translate as t
        t.preload_model = settings.value("preload", True, type=bool)
        t.unload_after_use = settings.value("unload", False, type=bool)
        self.preloadCheck.setChecked(t.preload_model)
        self.unloadCheck.setChecked(t.unload_after_use)
        # Restore from_lang first so updateToLang populates menuToLang,
        # then restore from_lang so it sticks as the final selection.
        from_idx = self.menuFromLang.findText(from_lang)
        if from_idx >= 0:
            self.menuFromLang.setCurrentIndex(from_idx)
        to_idx = self.menuToLang.findText(to_lang)
        if to_idx >= 0:
            self.menuToLang.setCurrentIndex(to_idx)

    def saveLanguageSettings(self):
        settings = QSettings("ITT", "ImageTranslationTool")
        settings.setValue("from_lang", self.menuFromLang.currentText())
        settings.setValue("to_lang", self.menuToLang.currentText())
        settings.setValue("preload", app.translate.preload_model)
        settings.setValue("unload", app.translate.unload_after_use)
        settings.sync()

    def onPreloadChanged(self, state):
        import app.translate as t
        t.preload_model = bool(state)

    def onUnloadChanged(self, state):
        import app.translate as t
        t.unload_after_use = bool(state)

    def preloadAtStartup(self):
        fromLang = self.LANG_CODES[self.menuFromLang.currentText()]
        toLang = self.LANG_CODES[self.menuToLang.currentText()]
        app.translate.preloadTranslationPkg(fromLang, toLang)

    def translateImage(self, fromLang, toLang):
        app.translate.initTranslationPkg(fromLang, toLang)
        self.outputDisplay.setPlainText(app.translate.translateText())
        self.show()

    def showOverlay(self):
        self.hide()
        self.overlay = SnipOverlay()

        fromLang = self.LANG_CODES[self.menuFromLang.currentText()]
        toLang = self.LANG_CODES[self.menuToLang.currentText()]

        self.overlay.captureComplete.connect(lambda: self.translateImage(fromLang, toLang))

        self.overlay.showFullScreen()

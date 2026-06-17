from PySide6.QtWidgets import (
    QMainWindow, QWidget, QFrame, QLabel, QStackedWidget,
    QHBoxLayout, QVBoxLayout, QGridLayout, QSizePolicy, QPushButton,
    QComboBox, QRadioButton, QButtonGroup, QGroupBox, QPlainTextEdit
)
from PySide6.QtCore import Qt
from app.overlay import SnipOverlay
from app.translate import initTranslationPkg, translateText

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

        languages = ["English", "Spanish", "German"]

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

        menuBarLayout.addWidget(capImageButton, 2, 0, 1, 3)

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

    def translateImage(self, fromLang, toLang):
        initTranslationPkg(fromLang, toLang)
        self.outputDisplay.setPlainText(translateText()) # Replace this with changing window output text box when implemented
        self.show()

    def showOverlay(self):
        self.hide()
        self.overlay = SnipOverlay()

        fromLang = self.LANG_CODES[self.menuFromLang.currentText()]
        toLang = self.LANG_CODES[self.menuToLang.currentText()]

        self.overlay.captureComplete.connect(lambda: self.translateImage(fromLang, toLang))

        self.overlay.showFullScreen()

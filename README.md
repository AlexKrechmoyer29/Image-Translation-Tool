# Image Translation Tool

Image Translation Tool is a tool designed to translate text from a selected region of the screen. It captures a screenshot, recognizes text with PaddleOCR, and translates the recognized text with Argos Translate.

The application is designed for quick, local translation of text visible in games, documents, browsers, and other desktop applications. Translation packages and OCR models are downloaded or loaded on demand, while the translation step itself runs locally after the required models are available.

## Features

- Select any rectangular region of the display with a full-screen capture overlay.
- Recognize and extract text with PaddleOCR.
- Translate to or from English with 49 supported languages.
- Model warmup at startup with `Pre-load Models`.
- Release translation model memory after each use with `Unload After Each Use`.
- Pinning the application window with `Pin Window`.
- Persistent language, model, and window preferences.

## Requirements

- Windows
- Python 3.10 or newer
- Internet access during dependency installation and when translation packages or model data must be downloaded

The pinned dependencies include PySide6, Argos Translate, PaddleOCR, PaddlePaddle, and NumPy. PaddlePaddle and PaddleOCR may require a substantial download and can take time to initialize on the first run.

## Installation

Install the pinned dependencies (Virtual environment recommended):

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The capture overlay writes the selected image to `app\Temp\temp.png`. Create that directory once if it does not already exist:

```powershell
New-Item -ItemType Directory -Force app\Temp
```

## Running the Application

```powershell
python main.py
```

To translate a screenshot:

1. Open the application.
2. Select the source language and target language.
3. Select `Capture Image`.
4. Drag across the text to translate.
5. Release the mouse button and wait for the translated text in `Output`.

Press `Esc` while the capture overlay is active to cancel the selection. A capture is submitted only when the screenshot is saved successfully.

`Currently, the OCR initialization process can take some time on first use. This is due to how PaddleOCR handles the gathering of its packages and models. This is a normal occurrence and usually speeds up on subsequent attempts.`

## Language Selection

The language selector intentionally restricts the available pairs:

- When the source language is not English, the target language is restricted to English.
- When English is the source language, the target selector exposes all languages listed by the application.
- When the target language is not English, the source selector is restricted to English.

The application maps the selected translation code to an OCR model. For example, Japanese uses PaddleOCR's `japan` model, Chinese uses `ch`, Arabic and Persian use `arabic`, and unlisted languages fall back to `latin`.

## Settings

| Setting | Behavior |
| --- | --- |
| `Pre-load Models` | Warms the selected Argos Translate package when the application starts. This can make the first translation faster but may delay startup. |
| `Unload After Each Use` | Releases loaded Argos Translate model state after translation to reduce retained memory. |
| `Pin Window` | Applies the always-on-top window flag. |

Language and model settings are stored through Qt `QSettings` under the `ITT` organization and `ImageTranslationTool` application name.

## Project Structure

```text
.
├── main.py                 # Application entry point
├── app/
│   ├── app_window.py       # Main window, settings, and Qt workers
│   ├── overlay.py          # Screen-selection overlay and screenshot capture
│   ├── translate.py        # OCR, Argos package lifecycle, and translation
│   └── testing.py          # Legacy standalone integration experiment
├── tests/                  # Automated unit and GUI-behavior tests
├── requirements.txt        # Pinned runtime dependencies
└── README.md
```

`app/testing.py` is not imported by the application. It performs package/model work at import time and is not part of the automated suite; use the files under `tests/` for repeatable verification.

## Testing

The test suite uses Python's standard-library `unittest` runner. It does not download translation packages, initialize PaddleOCR, access the network, or take a real screenshot. External services and the screen-capture boundary are replaced with deterministic test doubles.

Run the complete suite from the repository root:

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
```

Or, after activating the virtual environment:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

The suite currently verifies:

- OCR language-code mapping and Latin-script fallback.
- Argos package selection, installation, warmup, unloading, and translation calls.
- OCR result aggregation, Arabic text handling, translation logging, and unload behavior.
- Worker success and failure signals.
- Main-window defaults, language-pair constraints, settings writes, model toggles, pinning, overlay wiring, and asynchronous translation output.
- Overlay point tracking, Escape cancellation, normalized capture rectangles, save failures, and capture signals.

For headless environments, the Qt test helpers select Qt's `offscreen` platform automatically before creating the application object.

## Known Limitations

- Messy documents or unique fonts can cause incorrect text extraction.
- OCR initialization takes a considerable amount of time on first use
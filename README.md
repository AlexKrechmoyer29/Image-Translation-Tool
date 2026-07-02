# Image Translation Tool

A simple desktop app for translating text from screenshots. You select an area of the screen, the app runs OCR on the image, and then translates the detected text into the target language.

## What It Uses

- PySide6 for the desktop interface
- PaddleOCR for text recognition
- Argos Translate for offline translation

## Requirements

- Python 3.10 or newer
- Windows
- Internet access for package downloads

## Installation

1. Create and activate a virtual environment.
2. Install the dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python main.py
```

## How To Use

1. Open the app.
2. Choose the source language and the target language.
3. Click `Capture Image`.
4. Drag to select the part of the screen that contains text.
5. View the translated output in the app window.

## Settings

- `Pre-load Models` loads the translation model at startup.
- `Unload After Each Use` frees the translation model after each translation.
- `Pin Window` keeps the window above other windows.

## Project Structure

- `main.py` starts the app.
- `app/app_window.py` contains the main window and UI logic.
- `app/overlay.py` handles screen capture.
- `app/translate.py` handles OCR and translation.

## Notes

- The app stores temporary capture files under `app/Temp/`.
- The first translation for a language pair may take longer while packages are installed and loaded.

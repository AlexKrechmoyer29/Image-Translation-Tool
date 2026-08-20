# Image Translation Tool

Image Translation Tool captures a selected region of your screen, uses OCR to recognize the text in that region, and translates the result into your chosen language. It is intended for translating text shown in games, documents, browsers, and other desktop applications.

## Features

- Capture any rectangular region of the screen.
- Recognize text using PaddleOCR.
- Translate recognized text locally with Argos Translate.
- Select the source and target languages.
- Optionally keep the window on top and manage model memory.

## Requirements

- Windows
- Python 3.10 or newer
- Internet access for installing dependencies and downloading OCR or translation models when needed

## Installation

Install the dependencies from the project folder. A virtual environment is recommended:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Running the Application

```powershell
python main.py
```

To translate text:

1. Choose the source and target languages.
2. Select `Capture Image`.
3. Drag over the text you want to translate.
4. Release the mouse button and wait for the translated text in the output area.

Press `Esc` while selecting a region to cancel the capture.

`Currently, the OCR initialization process can take some time on first use. This is due to how PaddleOCR handles the gathering of its packages and models. This is a normal occurrence and usually speeds up on subsequent attempts.`

## AI

The AI option currently has no use in the application. It is a work in progress feature and does not affect the current OCR or translation process.

## Known Limitations

- Messy documents or unique fonts can cause incorrect text extraction.
- OCR initialization takes a considerable amount of time on first use.
- Current Argos model for translation can have inaccurate results.
- AI setting currently has no use and is WIP.

## Future Development

- Implement AI assistance on text extraction for messy documents.
- Pivot towards Google's Cloud Translation for faster and more accurate translation.
import argostranslate.package
import argostranslate.translate
from paddleocr import PaddleOCR
import os.path
import gc

# Map from translation language codes (ISO 639-1) to PaddleOCR lexicon codes.
# Languages not listed here default to "latin" (most European / Latin-script langs).
OCR_LANG_MAP = {
    "en": "en",
    "zh": "ch",                # Chinese simplified
    "zt": "chinese_cht",        # Chinese traditional
    "ja": "japan",
    "ko": "korean",
    "ar": "arabic",
    "fa": "arabic",             # Persian uses Arabic script
    "ur": "arabic",             # Urdu uses Arabic script
    "hi": "devanagari",
    "bn": "devanagari",         # Bengali
    "ta": "ta",                 # Tamil
    "te": "te",                 # Telugu
    "ru": "cyrillic",
    "uk": "cyrillic",
    "bg": "cyrillic",           # Bulgarian
    "sr": "cyrillic",           # Serbian
    "ky": "cyrillic",           # Kyrgyz
}

def getOcrLang(transLangCode):
    return OCR_LANG_MAP.get(transLangCode, "latin")

tempImg = ".\\app\\Temp\\temp.png"
tempLog = ".\\app\\Temp\\temp_log.txt"

# Model Loading Defaults
preload_model = True
unload_after_use = False

def initTranslationPkg(fromLang, toLang):
    global origLang  
    origLang = fromLang
    global transLang 
    transLang = toLang
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    package_to_install = next(
        filter(
            lambda x: x.from_code == origLang and x.to_code == transLang, available_packages
        )
    )
    argostranslate.package.install_from_path(package_to_install.download())
    return "Translation Packages Initialized"

def preloadTranslationPkg(fromLang, toLang):
    """Download/install the model and load it into RAM at startup."""
    initTranslationPkg(fromLang, toLang)
    # Trigger lazy model loading so the ctranslate2 model is in memory
    argostranslate.translate.translate(" ", fromLang, toLang)

def unloadTranslationPkg():
    """Unload the argos model from RAM after translation."""
    for item in argostranslate.translate.installed_translates:
        ct = item.cached_translation
        if ct and hasattr(ct, 'underlying') and hasattr(ct.underlying, 'translator'):
            translator = ct.underlying.translator
            if translator is not None:
                translator.unload_model()
            ct.underlying.translator = None
    argostranslate.translate.installed_translates.clear()
    gc.collect()

def translateText():
    ocr = PaddleOCR(use_angle_cls=True, lang=getOcrLang(origLang), use_gpu=False)
    result = ocr.ocr(tempImg, cls=True)

    if os.path.exists(tempLog):
        os.remove(tempLog)
    
    text = ""
    f = open(tempLog,"x")
    with open(tempLog, "a") as f:
        for line in result[0]:
            text += line[1][0] + " "
        if origLang == "ar":
            text = text[::-1]
        print(text + "\n")
        translation = argostranslate.translate.translate(text, origLang, transLang)
        f.write(translation + "\n")
        print(translation)

    # Unload model from RAM if the setting is enabled
    if unload_after_use:
        unloadTranslationPkg()

    return translation

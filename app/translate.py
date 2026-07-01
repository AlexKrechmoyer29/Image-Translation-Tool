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
    import argostranslate.package as argostranslate_package

    global origLang  
    origLang = fromLang
    global transLang 
    transLang = toLang
    argostranslate_package.update_package_index()
    available_packages = argostranslate_package.get_available_packages()
    package_to_install = next(
        filter(
            lambda x: x.from_code == origLang and x.to_code == transLang, available_packages
        )
    )
    argostranslate_package.install_from_path(package_to_install.download())
    return "Translation Packages Initialized"

def preloadTranslationPkg(fromLang, toLang):
    """Download/install the model and load it into RAM at startup."""
    import argostranslate.translate as argostranslate_translate

    initTranslationPkg(fromLang, toLang)
    # Trigger lazy model loading so the ctranslate2 model is in memory
    argostranslate_translate.translate(" ", fromLang, toLang)

def unloadTranslationPkg():
    """Unload the argos model from RAM after translation."""
    import argostranslate.translate as argostranslate_translate

    for item in argostranslate_translate.installed_translates:
        ct = item.cached_translation
        if ct and hasattr(ct, 'underlying') and hasattr(ct.underlying, 'translator'):
            translator = ct.underlying.translator
            if translator is not None:
                translator.unload_model()
            ct.underlying.translator = None
    argostranslate_translate.installed_translates.clear()
    gc.collect()

def translateText():
    import argostranslate.translate as argostranslate_translate
    from paddleocr import PaddleOCR

    ocr = PaddleOCR(use_angle_cls=True, lang=getOcrLang(origLang), use_gpu=False)
    result = ocr.ocr(tempImg, cls=True)

    if os.path.exists(tempLog):
        os.remove(tempLog)
    
    text = ""
    with open(tempLog, "x"):
        pass
    with open(tempLog, "a") as f:
        for line in result[0]:
            text += line[1][0] + " "
        if origLang == "ar":
            text = text[::-1]
        print(text + "\n")
        translation = argostranslate_translate.translate(text, origLang, transLang)
        f.write(translation + "\n")
        print(translation)

    # Unload model from RAM if the setting is enabled
    if unload_after_use:
        unloadTranslationPkg()

    return translation

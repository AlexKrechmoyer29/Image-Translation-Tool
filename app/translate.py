import argostranslate.package
import argostranslate.translate
from paddleocr import PaddleOCR
import os.path

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

def translateText():
    ocr = PaddleOCR(use_angle_cls=True, lang=origLang, use_gpu=False)
    result = ocr.ocr(".\\app\\Temp\\temp.png", cls=True)

    if os.path.exists(".\\app\\Temp\\temp_log.txt"):
        os.remove(".\\app\\Temp\\temp_log.txt")
    else:
        print("Entered else")
        f = open(".\\app\\Temp\\temp_log.txt","x")
        with open(".\\app\\Temp\\temp_log.txt", "a") as f:
            for line in result[0]:
                text = line[1][0]
                translation = argostranslate.translate.translate(text, origLang, transLang)
                f.write(translation + "\n")
                print(translation)
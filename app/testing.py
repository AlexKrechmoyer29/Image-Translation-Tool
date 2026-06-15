import argostranslate.package
import argostranslate.translate
from paddleocr import PaddleOCR
import PySide6.QtCore

fromLang = "en"
toLang = "es"

argostranslate.package.update_package_index()
available_packages = argostranslate.package.get_available_packages()
package_to_install = next(
    filter(
        lambda x: x.from_code == fromLang and x.to_code == toLang, available_packages
    )
)
argostranslate.package.install_from_path(package_to_install.download())

ocr = PaddleOCR(use_angle_cls=True, lang=fromLang, use_gpu=False)

result = ocr.ocr("./document.jpg", cls=True)

for line in result[0]:
    text = line[1][0]
    translation = argostranslate.translate.translate(text, fromLang, toLang)
    # confidence = line[1][1]
    print(translation)
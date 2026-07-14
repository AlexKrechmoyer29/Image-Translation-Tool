import builtins
import gc
import sys
import types
import unittest
from unittest.mock import MagicMock, mock_open, patch

import app.translate as translate


class TranslateUtilityTests(unittest.TestCase):
    def test_get_ocr_language_uses_script_specific_mappings(self):
        expected = {
            "en": "en",
            "zh": "ch",
            "zt": "chinese_cht",
            "ja": "japan",
            "ko": "korean",
            "ar": "arabic",
            "fa": "arabic",
            "hi": "devanagari",
            "ru": "cyrillic",
        }

        for code, ocr_code in expected.items():
            with self.subTest(code=code):
                self.assertEqual(translate.getOcrLang(code), ocr_code)

    def test_get_ocr_language_defaults_to_latin(self):
        self.assertEqual(translate.getOcrLang("es"), "latin")
        self.assertEqual(translate.getOcrLang("unknown"), "latin")

    def test_init_translation_package_downloads_matching_package(self):
        package = MagicMock(from_code="es", to_code="en")
        package.download.return_value = "downloaded-package"
        package_module = types.ModuleType("argostranslate.package")
        package_module.update_package_index = MagicMock()
        package_module.get_available_packages = MagicMock(return_value=[package])
        package_module.install_from_path = MagicMock()
        argos_module = types.ModuleType("argostranslate")

        with patch.dict(
            sys.modules,
            {
                "argostranslate": argos_module,
                "argostranslate.package": package_module,
            },
        ):
            result = translate.initTranslationPkg("es", "en")

        self.assertEqual(result, "Translation Packages Initialized")
        self.assertEqual(translate.origLang, "es")
        self.assertEqual(translate.transLang, "en")
        package_module.update_package_index.assert_called_once_with()
        package_module.get_available_packages.assert_called_once_with()
        package.download.assert_called_once_with()
        package_module.install_from_path.assert_called_once_with("downloaded-package")

    def test_preload_translation_package_initializes_then_warms_model(self):
        argos_translate = types.ModuleType("argostranslate.translate")
        argos_translate.translate = MagicMock(return_value=" ")
        argos_module = types.ModuleType("argostranslate")

        with patch.object(translate, "initTranslationPkg") as initialize:
            with patch.dict(
                sys.modules,
                {
                    "argostranslate": argos_module,
                    "argostranslate.translate": argos_translate,
                },
            ):
                result = translate.preloadTranslationPkg("es", "en")

        self.assertIsNone(result)
        initialize.assert_called_once_with("es", "en")
        argos_translate.translate.assert_called_once_with(" ", "es", "en")

    def test_unload_translation_package_unloads_models_and_clears_registry(self):
        loaded_translator = MagicMock()
        cached_translation = types.SimpleNamespace(
            underlying=types.SimpleNamespace(translator=loaded_translator)
        )
        missing_translator = types.SimpleNamespace(
            cached_translation=types.SimpleNamespace(underlying=None)
        )
        installed = [
            types.SimpleNamespace(cached_translation=cached_translation),
            missing_translator,
        ]
        argos_translate = types.ModuleType("argostranslate.translate")
        argos_translate.installed_translates = installed
        argos_module = types.ModuleType("argostranslate")

        with patch.dict(
            sys.modules,
            {
                "argostranslate": argos_module,
                "argostranslate.translate": argos_translate,
            },
        ), patch.object(gc, "collect") as collect:
            result = translate.unloadTranslationPkg()

        self.assertIsNone(result)
        loaded_translator.unload_model.assert_called_once_with()
        self.assertIsNone(cached_translation.underlying.translator)
        self.assertEqual(argos_translate.installed_translates, [])
        collect.assert_called_once_with()

    def test_translate_text_runs_ocr_writes_log_and_returns_translation(self):
        ocr = MagicMock()
        ocr.ocr.return_value = [
            [([0, 0], ("Hello", 0.99)), ([0, 0], ("world", 0.95))]
        ]
        paddleocr = types.ModuleType("paddleocr")
        paddleocr.PaddleOCR = MagicMock(return_value=ocr)
        argos_translate = types.ModuleType("argostranslate.translate")
        argos_translate.translate = MagicMock(return_value="Hola mundo")
        argos_module = types.ModuleType("argostranslate")
        log_file = mock_open()

        old_orig, old_trans = getattr(translate, "origLang", None), getattr(
            translate, "transLang", None
        )
        translate.origLang = "es"
        translate.transLang = "en"
        try:
            with patch.dict(
                sys.modules,
                {
                    "paddleocr": paddleocr,
                    "argostranslate": argos_module,
                    "argostranslate.translate": argos_translate,
                },
            ), patch.object(translate.os.path, "exists", return_value=False), patch(
                "builtins.open", log_file
            ):
                result = translate.translateText()
        finally:
            translate.origLang, translate.transLang = old_orig, old_trans

        self.assertEqual(result, "Hola mundo")
        paddleocr.PaddleOCR.assert_called_once_with(
            use_angle_cls=True, lang="latin", use_gpu=False
        )
        ocr.ocr.assert_called_once_with(translate.tempImg, cls=True)
        argos_translate.translate.assert_called_once_with("Hello world ", "es", "en")
        log_file.assert_any_call(translate.tempLog, "x")
        log_file.assert_any_call(translate.tempLog, "a")
        log_file().write.assert_called_once_with("Hola mundo\n")

    def test_translate_text_reverses_arabic_ocr_and_unloads_when_enabled(self):
        ocr = MagicMock()
        ocr.ocr.return_value = [[[[0, 0], ("مرحبا", 0.99)]]]
        paddleocr = types.ModuleType("paddleocr")
        paddleocr.PaddleOCR = MagicMock(return_value=ocr)
        argos_translate = types.ModuleType("argostranslate.translate")
        argos_translate.translate = MagicMock(return_value="translated")
        argos_module = types.ModuleType("argostranslate")

        old_orig, old_trans = getattr(translate, "origLang", None), getattr(
            translate, "transLang", None
        )
        old_unload = translate.unload_after_use
        translate.origLang = "ar"
        translate.transLang = "en"
        translate.unload_after_use = True
        try:
            with patch.dict(
                sys.modules,
                {
                    "paddleocr": paddleocr,
                    "argostranslate": argos_module,
                    "argostranslate.translate": argos_translate,
                },
            ), patch.object(translate.os.path, "exists", return_value=False), patch(
                "builtins.open", mock_open()
            ), patch("builtins.print"), patch.object(
                translate, "unloadTranslationPkg"
            ) as unload:
                result = translate.translateText()
        finally:
            translate.origLang, translate.transLang = old_orig, old_trans
            translate.unload_after_use = old_unload

        self.assertEqual(result, "translated")
        argos_translate.translate.assert_called_once_with("مرحبا "[::-1], "ar", "en")
        unload.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()

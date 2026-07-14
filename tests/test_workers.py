import types
import unittest
from unittest.mock import MagicMock, patch

from tests.qt_support import get_application

get_application()

from app.app_window import TranslationWarmupWorker, TranslationWorker, _translate_module


class WorkerTests(unittest.TestCase):
    def test_translate_module_imports_module_and_applies_runtime_settings(self):
        fake_module = MagicMock()
        with patch("importlib.import_module", return_value=fake_module) as importer:
            result = _translate_module(True, False)

        self.assertIs(result, fake_module)
        importer.assert_called_once_with("app.translate")
        self.assertTrue(fake_module.preload_model)
        self.assertFalse(fake_module.unload_after_use)

    def test_translate_module_can_leave_settings_unchanged(self):
        fake_module = types.SimpleNamespace()
        with patch("importlib.import_module", return_value=fake_module):
            _translate_module()

        self.assertFalse(hasattr(fake_module, "preload_model"))
        self.assertFalse(hasattr(fake_module, "unload_after_use"))

    def test_warmup_worker_emits_finished_after_preloading(self):
        fake_translate = MagicMock()
        finished = []
        failed = []
        worker = TranslationWarmupWorker("es", "en", True, False)
        worker.finished.connect(lambda: finished.append(True))
        worker.failed.connect(failed.append)

        with patch("app.app_window._translate_module", return_value=fake_translate):
            worker.run()

        fake_translate.preloadTranslationPkg.assert_called_once_with("es", "en")
        self.assertEqual(finished, [True])
        self.assertEqual(failed, [])

    def test_warmup_worker_emits_failure_message_when_preloading_fails(self):
        fake_translate = MagicMock()
        fake_translate.preloadTranslationPkg.side_effect = RuntimeError("network down")
        finished = []
        failed = []
        worker = TranslationWarmupWorker("es", "en", True, False)
        worker.finished.connect(lambda: finished.append(True))
        worker.failed.connect(failed.append)

        with patch("app.app_window._translate_module", return_value=fake_translate):
            worker.run()

        self.assertEqual(finished, [])
        self.assertEqual(failed, ["network down"])

    def test_translation_worker_initializes_package_and_emits_result(self):
        fake_translate = MagicMock()
        fake_translate.translateText.return_value = "translated text"
        finished = []
        failed = []
        worker = TranslationWorker("es", "en", False, True)
        worker.finished.connect(finished.append)
        worker.failed.connect(failed.append)

        with patch("app.app_window._translate_module", return_value=fake_translate):
            worker.run()

        fake_translate.initTranslationPkg.assert_called_once_with("es", "en")
        fake_translate.translateText.assert_called_once_with()
        self.assertEqual(finished, ["translated text"])
        self.assertEqual(failed, [])

    def test_translation_worker_emits_failure_without_finished_signal(self):
        fake_translate = MagicMock()
        fake_translate.initTranslationPkg.side_effect = ValueError("package missing")
        finished = []
        failed = []
        worker = TranslationWorker("es", "en", False, False)
        worker.finished.connect(finished.append)
        worker.failed.connect(failed.append)

        with patch("app.app_window._translate_module", return_value=fake_translate):
            worker.run()

        self.assertEqual(finished, [])
        self.assertEqual(failed, ["package missing"])


if __name__ == "__main__":
    unittest.main()

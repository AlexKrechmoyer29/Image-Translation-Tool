import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QStyleFactory

from tests.qt_support import get_application, wait_for

application = get_application()

from app import translate
from app.app_window import MainWindow, apply_style


class MainWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.settings_dir = tempfile.TemporaryDirectory()
        cls.original_format = QSettings.defaultFormat()
        QSettings.setDefaultFormat(QSettings.IniFormat)
        QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, cls.settings_dir.name)

    @classmethod
    def tearDownClass(cls):
        QSettings.setDefaultFormat(cls.original_format)
        cls.settings_dir.cleanup()

    def setUp(self):
        self._clear_settings()
        self._settings_patch = patch(
            "app.app_window.QSettings", side_effect=self._isolated_settings
        )
        self._settings_patch.start()
        self.window = MainWindow()

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()
        application.processEvents()
        self._settings_patch.stop()
        self._clear_settings()

    def _isolated_settings(self, *args, **kwargs):
        return QSettings(
            QSettings.IniFormat,
            QSettings.UserScope,
            "ITT",
            "ImageTranslationTool",
        )

    def _clear_settings(self):
        settings = QSettings(
            QSettings.IniFormat,
            QSettings.UserScope,
            "ITT",
            "ImageTranslationTool",
        )
        settings.clear()
        settings.sync()

    def test_apply_style_uses_fusion_and_a_dark_palette(self):
        apply_style(application)

        self.assertEqual(application.style().objectName().lower(), "fusion")
        self.assertEqual(application.palette().window().color().red(), 53)
        self.assertEqual(application.palette().base().color().red(), 42)

    def test_default_language_pair_is_spanish_to_english(self):
        self.assertEqual(self.window.menuFromLang.currentText(), "Spanish")
        self.assertEqual(self.window.menuToLang.currentText(), "English")
        self.assertEqual(self.window.menuToLang.count(), 1)
        self.assertTrue(self.window.preloadCheck.isChecked())
        self.assertFalse(self.window.unloadCheck.isChecked())

    def test_selecting_english_as_source_enables_all_target_languages(self):
        self.window.menuFromLang.setCurrentText("English")
        application.processEvents()

        self.assertEqual(self.window.menuToLang.count(), len(MainWindow.LANG_CODES))
        self.assertIn("Spanish", [
            self.window.menuToLang.itemText(index)
            for index in range(self.window.menuToLang.count())
        ])

    def test_non_english_target_restricts_source_to_english(self):
        self.window.menuFromLang.setCurrentText("English")
        self.window.menuToLang.setCurrentText("French")
        application.processEvents()

        self.assertEqual(self.window.menuFromLang.count(), 1)
        self.assertEqual(self.window.menuFromLang.currentText(), "English")

    def test_language_and_model_settings_round_trip_through_qsettings(self):
        self.window.menuFromLang.setCurrentText("English")
        self.window.menuToLang.setCurrentText("German")
        self.window.preloadCheck.setChecked(False)
        self.window.unloadCheck.setChecked(True)
        self.window.pinCheck.setChecked(True)
        self.window.saveLanguageSettings()
        self.assertTrue(self._isolated_settings().value("pin_window", False, type=bool))
        self.window.close()
        self.window.deleteLater()
        application.processEvents()

        restored = MainWindow()
        try:
            self.assertEqual(restored.menuFromLang.currentText(), "English")
            self.assertEqual(restored.menuToLang.currentText(), "German")
            self.assertFalse(restored.preloadCheck.isChecked())
            self.assertTrue(restored.unloadCheck.isChecked())
        finally:
            restored.close()
            restored.deleteLater()
            application.processEvents()

    def test_pin_toggle_applies_window_stays_on_top_flag(self):
        self.window.pinCheck.setChecked(True)

        self.assertTrue(self.window.windowFlags() & Qt.WindowStaysOnTopHint)


    def test_checkbox_changes_update_loaded_translation_module(self):
        old_preload = translate.preload_model
        old_unload = translate.unload_after_use
        try:
            self.window.preloadCheck.setChecked(False)
            self.window.unloadCheck.setChecked(True)

            self.assertFalse(translate.preload_model)
            self.assertTrue(translate.unload_after_use)
        finally:
            translate.preload_model = old_preload
            translate.unload_after_use = old_unload

    def test_translate_image_shows_processing_then_translated_output(self):
        fake_translate = MagicMock()
        fake_translate.translateText.return_value = "Hallo Welt"

        with patch("app.app_window._translate_module", return_value=fake_translate):
            self.window.translateImage("en", "de")
            self.assertEqual(self.window.outputDisplay.toPlainText(), "Processing screenshot...")
            self.assertTrue(wait_for(lambda: self.window._translation_thread is None))

        self.assertEqual(self.window.outputDisplay.toPlainText(), "Hallo Welt")
        fake_translate.initTranslationPkg.assert_called_once_with("en", "de")
        fake_translate.translateText.assert_called_once_with()

    def test_translate_image_displays_worker_error(self):
        fake_translate = MagicMock()
        fake_translate.translateText.side_effect = RuntimeError("OCR unavailable")

        with patch("app.app_window._translate_module", return_value=fake_translate):
            self.window.translateImage("en", "de")
            self.assertTrue(wait_for(lambda: self.window._translation_thread is None))

        self.assertEqual(
            self.window.outputDisplay.toPlainText(),
            "Translation failed:\nOCR unavailable",
        )

    def test_translate_image_ignores_duplicate_request_while_thread_is_active(self):
        self.window.outputDisplay.setPlainText("existing output")
        self.window._translation_thread = object()

        with patch.object(self.window, "show") as show:
            self.window.translateImage("en", "de")

        show.assert_called_once_with()
        self.assertEqual(self.window.outputDisplay.toPlainText(), "existing output")
        self.window._translation_thread = None

    def test_show_overlay_hides_window_and_translates_selected_language_codes(self):
        from PySide6.QtWidgets import QWidget
        from PySide6.QtCore import Signal

        class FakeOverlay(QWidget):
            captureComplete = Signal()

            def __init__(self):
                super().__init__()
                self.was_shown = False

            def showFullScreen(self):
                self.was_shown = True

        self.window.menuFromLang.setCurrentText("English")
        self.window.menuToLang.setCurrentText("Spanish")
        with patch("app.app_window.SnipOverlay", FakeOverlay), patch.object(
            self.window, "hide"
        ) as hide, patch.object(self.window, "translateImage") as translate_image:
            self.window.showOverlay()
            self.window.overlay.captureComplete.emit()

        hide.assert_called_once_with()
        self.assertTrue(self.window.overlay.was_shown)
        translate_image.assert_called_once_with("en", "es")
        self.window.overlay.close()

    def test_overlay_close_restores_window_only_when_translation_is_idle(self):
        with patch.object(self.window, "show") as show, patch.object(
            self.window, "raise_"
        ) as raise_window, patch.object(self.window, "activateWindow") as activate:
            self.window._restoreWindowAfterOverlay()

        show.assert_called_once_with()
        raise_window.assert_called_once_with()
        activate.assert_called_once_with()

        self.window._translation_thread = object()
        with patch.object(self.window, "show") as show:
            self.window._restoreWindowAfterOverlay()
        show.assert_not_called()
        self.window._translation_thread = None


if __name__ == "__main__":
    unittest.main()

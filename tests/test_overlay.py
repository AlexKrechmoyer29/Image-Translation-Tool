import os
import unittest
from unittest.mock import MagicMock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPointF, QRect, Qt
from PySide6.QtGui import QGuiApplication

from tests.qt_support import get_application

application = get_application()

from app.overlay import SnipOverlay


class MouseEvent:
    def __init__(self, x, y):
        self._position = QPointF(x, y)

    def position(self):
        return self._position


class KeyEvent:
    def __init__(self, key):
        self._key = key

    def key(self):
        return self._key


class OverlayTests(unittest.TestCase):
    def setUp(self):
        self.overlay = SnipOverlay()

    def tearDown(self):
        self.overlay.close()
        self.overlay.deleteLater()
        application.processEvents()

    def test_mouse_press_and_move_store_selection_points(self):
        self.overlay.mousePressEvent(MouseEvent(120, 80))
        with patch("app.overlay.QTimer.singleShot") as single_shot:
            self.overlay.mouseMoveEvent(MouseEvent(20, 30))

        self.assertEqual(self.overlay.startPoint, QPointF(120, 80))
        self.assertEqual(self.overlay.endPoint, QPointF(20, 30))
        single_shot.assert_called_once_with(30, self.overlay.update)

    def test_escape_closes_overlay(self):
        with patch.object(self.overlay, "close") as close:
            self.overlay.keyPressEvent(KeyEvent(Qt.Key_Escape))

        close.assert_called_once_with()

    def test_mouse_release_schedules_capture_after_selection(self):
        self.overlay.startPoint = QPointF(120, 80)
        self.overlay.endPoint = QPointF(20, 30)
        with patch.object(self.overlay, "hide") as hide, patch(
            "app.overlay.QTimer.singleShot"
        ) as single_shot:
            self.overlay.mouseReleaseEvent(MouseEvent(20, 30))

        hide.assert_called_once_with()
        single_shot.assert_called_once_with(100, self.overlay.captureSelection)

    def test_capture_selection_saves_normalized_rectangle_and_emits_success(self):
        self.overlay.startPoint = QPointF(120, 80)
        self.overlay.endPoint = QPointF(20, 30)
        pixmap = MagicMock()
        pixmap.save.return_value = True
        screen = MagicMock()
        screen.grabWindow.return_value = pixmap
        emitted = []
        self.overlay.captureComplete.connect(lambda: emitted.append(True))

        with patch.object(QGuiApplication, "primaryScreen", return_value=screen), patch.object(
            self.overlay, "close"
        ) as close:
            self.overlay.captureSelection()

        expected = QRect(
            self.overlay.startPoint.toPoint(), self.overlay.endPoint.toPoint()
        ).normalized()
        screen.grabWindow.assert_called_once_with(
            0, expected.x(), expected.y(), expected.width(), expected.height()
        )
        pixmap.save.assert_called_once_with(os.path.join("app\\Temp\\", "temp.png"))
        self.assertEqual(emitted, [True])
        close.assert_called_once_with()

    def test_capture_selection_closes_without_emitting_when_save_fails(self):
        self.overlay.startPoint = QPointF(10, 20)
        self.overlay.endPoint = QPointF(40, 70)
        pixmap = MagicMock()
        pixmap.save.return_value = False
        screen = MagicMock()
        screen.grabWindow.return_value = pixmap
        emitted = []
        self.overlay.captureComplete.connect(lambda: emitted.append(True))

        with patch.object(QGuiApplication, "primaryScreen", return_value=screen), patch.object(
            self.overlay, "close"
        ) as close:
            self.overlay.captureSelection()

        self.assertEqual(emitted, [])
        close.assert_called_once_with()

    def test_close_event_accepts_close_without_emitting_capture(self):
        event = MagicMock()
        emitted = []
        self.overlay.captureComplete.connect(lambda: emitted.append(True))

        self.overlay.closeEvent(event)

        event.accept.assert_called_once_with()
        self.assertEqual(emitted, [])


if __name__ == "__main__":
    unittest.main()

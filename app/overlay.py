import os, sys
from PySide6.QtCore import QRect, Qt, QTimer
from PySide6.QtGui import QGuiApplication, QPainter, QPen, QColor
from PySide6.QtWidgets import QWidget, QApplication

class SnipOverlay(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.startPoint = None
        self.endPoint = None
        self.save_path = None

    def mousePressEvent(self, event):
        self.startPoint = event.position()
    
    def mouseMoveEvent(self, event):
        self.endPoint = event.position()
        self.update()
    
    def mouseReleaseEvent(self, event):
        print(f"Starting point (X,Y): ({self.startPoint.x()}, {self.startPoint.y()})")
        print(f"Ending Point (X,Y): ({self.endPoint.x()}, {self.endPoint.y()})")
        self.hide()
        QTimer.singleShot(100, self.captureSelection)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 80))

        if self.startPoint is None or self.endPoint is None:
            return

        rectangle = QRect(
            self.startPoint.toPoint(),
            self.endPoint.toPoint()
        ).normalized()
        pen = QPen(QColor("cyan"))
        pen.setWidth(8)

        painter.setPen(pen)
        painter.drawRect(rectangle)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def captureSelection(self):
        rectangle = QRect(
            self.startPoint.toPoint(),
            self.endPoint.toPoint()
        ).normalized()

        screen = QGuiApplication.primaryScreen()
        pixmap = screen.grabWindow(0, rectangle.x(), rectangle.y(), rectangle.width(), rectangle.height())
        self.save_path = os.path.join("app\\Temp\\", "temp.png")
        success = pixmap.save(self.save_path)
        print(f"Saved successfully: {success} | Path: {self.save_path}")
        QApplication.quit()
        
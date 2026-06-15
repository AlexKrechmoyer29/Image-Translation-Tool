from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtCore import QRect
from PySide6.QtGui import QPainter

class SnipOverlay(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.startPoint = None
        self.endPoint = None

    def mousePressEvent(self, event):
        self.startPoint = event.position()
    
    def mouseMoveEvent(self, event):
        self.endPoint = event.position()
        self.update()
    
    def mouseReleaseEvent(self, event):
        print(f"Starting point (X,Y): ({self.startPoint.x()}, {self.startPoint.y()})")
        print(f"Ending Point (X,Y): ({self.endPoint.x()}, {self.endPoint.y()})")

    def paintEvent(self, event):
        if self.startPoint is None or self.endPoint is None:
            return

        painter = QPainter(self)

        rectangle = QRect(
            self.startPoint.toPoint(),
            self.endPoint.toPoint()
        ).normalized()

        painter.drawRect(rectangle)
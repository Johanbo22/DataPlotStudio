import sys
from PyQt6.QtCore import QTimer, Qt, QElapsedTimer, QPropertyAnimation, QRect, QEasingCurve
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout
from PyQt6.QtGui import QPainter, QFont, QColor, QPen
from lupa import LuaRuntime

class SavedProjectAnimation(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(400, 400)
        
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute(open("ui/animation_scripts/saved_project_tickmark.lua").read())
        
        self.timer = QTimer(self)
        self.clock = QElapsedTimer()
        self.timer.setInterval(16)
        self.timer.timeout.connect(self.update_frame)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self.close_timer = QTimer(self)
        self.close_timer.setSingleShot(True)
        self.close_timer.timeout.connect(self.close)

        self.pop_animation = QPropertyAnimation(self, b"geometry")
        self.pop_animation.setDuration(450)
        self.pop_animation.setEasingCurve(QEasingCurve.Type.OutElastic)

        self.positions = []
        self.running = False
        self.is_complete = False

    def start_animation(self):
        if self.running:
            return
        
        self.lua.globals().reset()
        self.clock.restart()
        self.running = True
        self.timer.start()

        self.close_timer.start(1500)

    def update_frame(self):
        dt = self.clock.restart() / 1000.0
        self.lua.globals().update(dt)

        result = self.lua.globals().get_frame()
        self.is_complete = bool(result["complete"])

        self.positions.clear()

        lua_positions = result["positions"]
        i = 1
        while lua_positions[i] is not None:
            self.positions.append(dict(lua_positions[i].items()))
            i += 1

        if self.is_complete:
            self.timer.stop()
            self.running = False

        self.update()

    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.fillRect(self.rect(), QColor(30, 30, 40))
        painter.translate(200, 200)

        painter.setPen(QPen(QColor(100, 255, 100), 4))
        painter.setBrush(Qt.BrushStyle.NoBrush)

        for pos in self.positions:
            t = pos["type"]

            if t == "text":
                painter.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
                painter.setPen(QColor(150, 255, 150))
                painter.drawText(int(pos["x"] - 80), int(pos["y"]), pos["text"])
            
            elif t == "circle":
                painter.drawEllipse(
                    int(pos["x"] - 2),
                    int(pos["y"] - 2),
                    4,
                    4
                )

            elif t == "line":
                painter.drawLine(
                    int(pos["x1"]), int(pos["y1"]),
                    int(pos["x2"]), int(pos["y2"])
                )
    
    def showEvent(self, event):
        super().showEvent(event)

        screen = self.screen().availableGeometry()
        end_rect = QRect(
            screen.center().x() - self.width() // 2,
            screen.center().y() - self.height() // 2,
            self.width(),
            self.height()
        )

        start_rect = QRect(
            end_rect.center().x() - int(self.width() * 0.4),
            end_rect.center().y() - int(self.height() * 0.4),
            int(self.width() * 0.8),
            int(self.height() * 0.8)
        )

        self.setGeometry(start_rect)

        self.pop_animation.stop()
        self.pop_animation.setStartValue(start_rect)
        self.pop_animation.setEndValue(end_rect)
        self.pop_animation.start()
import sys
import random
import math
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, 
                             QVBoxLayout, QSlider, QLabel, QGroupBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QFont

class GameWidget(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.ball_pos = [400, 300]
        self.ball_vel = [random.choice([-6, 6]), random.choice([-6, 6])]
        self.mouse_pos = (-500, -500)
        self.score = 0
        
        self.setMouseTracking(True)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game)
        self.timer.start(16)

    def update_game(self):
        self.ball_pos[0] += self.ball_vel[0]
        self.ball_pos[1] += self.ball_vel[1]
        
        if self.ball_pos[0] <= 0 or self.ball_pos[0] >= self.width(): self.ball_vel[0] *= -1
        if self.ball_pos[1] <= 0 or self.ball_pos[1] >= self.height(): self.ball_vel[1] *= -1
        self.update()

    def mouseMoveEvent(self, event):
        self.mouse_pos = (event.position().x(), event.position().y())

    def mousePressEvent(self, event):
        radius = self.parent_window.radius_slider.value()
        dist = math.hypot(event.position().x() - self.ball_pos[0], 
                          event.position().y() - self.ball_pos[1])
        if dist <= radius:
            self.score += 1
            self.ball_vel = [random.choice([-10, 10]), random.choice([-10, 10])]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0)) # Черный фон
        
        # Отрисовка счета
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        painter.drawText(20, 40, f"Очки: {self.score}")
        
        radius = self.parent_window.radius_slider.value()
        
        # 1. Видимый контур радиуса фонарика
        painter.setPen(QPen(QColor(255, 255, 255, 80), 1, Qt.PenStyle.DashLine))
        painter.drawEllipse(int(self.mouse_pos[0] - radius), int(self.mouse_pos[1] - radius), radius * 2, radius * 2)
        
        # 2. Мяч (если внутри)
        dist = math.hypot(self.mouse_pos[0] - self.ball_pos[0], self.mouse_pos[1] - self.ball_pos[1])
        if dist <= radius:
            painter.setBrush(QColor(255, 255, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(int(self.ball_pos[0]-10), int(self.ball_pos[1]-10), 20, 20)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Световой Мяч")
        self.resize(600, 450)
        
        tabs = QTabWidget()
        
        # Компактная вкладка настроек
        settings_tab = QWidget()
        layout = QVBoxLayout()
        
        group = QGroupBox("Параметры игры")
        group_layout = QVBoxLayout()
        
        self.radius_slider = QSlider(Qt.Orientation.Horizontal)
        self.radius_slider.setRange(30, 100)
        self.radius_slider.setValue(60)
        
        group_layout.addWidget(QLabel("Радиус фонарика (пиксели):"))
        group_layout.addWidget(self.radius_slider)
        group.setLayout(group_layout)
        
        layout.addWidget(group)
        layout.addStretch() # Прижимает группу к верху
        settings_tab.setLayout(layout)
        
        tabs.addTab(settings_tab, "⚙ Настройки")
        tabs.addTab(GameWidget(self), "🎮 Старт")
        self.setCentralWidget(tabs)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
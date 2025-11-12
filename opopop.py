# src/main.py
import sys
import math
import random
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import QTimer, Qt, QPointF
from PySide6.QtGui import QPainter, QColor

# --------- Simulation classes ---------
class Airplane:
    def __init__(self, id_, x, y, altitude=3000, speed=150, heading=180):
        self.id = id_
        self.x = x
        self.y = y
        self.altitude = altitude
        self.speed = speed  # units per second (map units)
        self.heading = heading  # degrees (0 = east, 90 = north)
        self.fuel = 100.0
        self.status = "flying"
    def update(self, dt):
        # dt in seconds
        rad = math.radians(self.heading)
        self.x += math.cos(rad) * self.speed * dt
        self.y -= math.sin(rad) * self.speed * dt  # y-axis screen inversé
        self.fuel -= 0.01 * dt * (self.speed/100)
        if self.fuel <= 0:
            self.status = "out_of_fuel"
    def change_heading(self, new_heading):
        self.heading = new_heading % 360
    def change_altitude(self, delta):
        self.altitude = max(0, self.altitude + delta)
    def to_tuple(self):
        return (self.x, self.y)

class Airspace:
    def __init__(self, w, h):
        self.width = w
        self.height = h
        self.airplanes = []
        self.next_id = 1
        # runway center
        self.runway = (w*0.85, h*0.5, 80)  # x,y,radius
    def spawn_airplane(self):
        x = 0
        y = random.uniform(50, self.height - 50)
        heading = 0  # east->west if x=0 then heading ~0 to go right; adjust as you like
        ap = Airplane(self.next_id, x, y, altitude=3000, speed=random.uniform(80,160), heading=0)
        self.next_id += 1
        self.airplanes.append(ap)
    def update(self, dt):
        for ap in list(self.airplanes):
            ap.update(dt)
            # remove if out of bounds
            if not ( -100 < ap.x < self.width + 100 and -100 < ap.y < self.height + 100):
                try:
                    self.airplanes.remove(ap)
                except ValueError:
                    pass
    def detect_collisions(self, d_plan=40, d_alt=300):
        pairs = []
        n = len(self.airplanes)
        for i in range(n):
            a = self.airplanes[i]
            for j in range(i+1, n):
                b = self.airplanes[j]
                dx = a.x - b.x
                dy = a.y - b.y
                d = math.hypot(dx, dy)
                if d < d_plan and abs(a.altitude - b.altitude) < d_alt:
                    pairs.append((a,b))
        return pairs

# --------- UI classes ---------
class CanvasWidget(QWidget):
    def __init__(self, airspace):
        super().__init__()
        self.airspace = airspace
        self.setMinimumSize(800, 600)
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # background
        painter.fillRect(self.rect(), QColor(20, 30, 40))
        # runway
        rx, ry, rr = self.airspace.runway
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(80,80,85))
        painter.drawEllipse(QPointF(rx, ry), rr, rr/3)
        # airplanes
        for ap in self.airspace.airplanes:
            x = ap.x
            y = ap.y
            # draw as triangle
            painter.save()
            painter.translate(x, y)
            painter.rotate(-ap.heading)  # rotate to heading
            painter.setBrush(QColor(200,200,60))
            painter.drawPolygon(
                QPointF(0,-6), QPointF(10,0), QPointF(0,6)
            )
            painter.restore()
            # label id
            painter.setPen(QColor(220,220,220))
            painter.drawText(x+8, y-8, f"#{ap.id} {int(ap.altitude)}m")
        painter.end()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AirControl - Simulation")
        self.airspace = Airspace(1200, 800)
        self.canvas = CanvasWidget(self.airspace)
        self.info = QLabel("Press Start")
        # controls
        self.btn_start = QPushButton("Start")
        self.btn_start.clicked.connect(self.start)
        self.btn_spawn = QPushButton("Spawn")
        self.btn_spawn.clicked.connect(self.airspace.spawn_airplane)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.info)
        layout.addWidget(self.btn_start)
        layout.addWidget(self.btn_spawn)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        # timer
        self.timer = QTimer(self)
        self.timer.setInterval(50)  # ms
        self.timer.timeout.connect(self.tick)
        self.elapsed = 0.0
    def start(self):
        if not self.timer.isActive():
            self.timer.start()
            self.btn_start.setText("Pause")
        else:
            self.timer.stop()
            self.btn_start.setText("Start")
    def tick(self):
        dt = self.timer.interval() / 1000.0
        self.elapsed += dt
        # spawn occasionally
        if random.random() < 0.02:
            self.airspace.spawn_airplane()
        self.airspace.update(dt)
        collisions = self.airspace.detect_collisions(d_plan=30, d_alt=300)
        if collisions:
            self.info.setText(f"Collision alert! pairs: {len(collisions)}")
        else:
            self.info.setText(f"Planes: {len(self.airspace.airplanes)}  Time: {int(self.elapsed)}s")
        self.canvas.update()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

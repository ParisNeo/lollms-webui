import sys
import time
import pipmaster as pm
if not pm.is_installed("PyQt5"):
    pm.install("PyQt5")

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QSlider
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from pathlib import Path

class MetronomeWorker(QThread):
    tick = pyqtSignal()

    def __init__(self, bpm):
        super().__init__()
        self.bpm = bpm
        self.running = False

    def run(self):
        self.running = True
        interval = 60.0 / self.bpm
        while self.running:
            self.tick.emit()
            time.sleep(interval)

    def stop(self):
        self.running = False
        self.wait()

class MetronomeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('PyQt Metronome')
        self.setGeometry(100, 100, 200, 150)

        self.layout = QVBoxLayout()

        self.label = QLabel('BPM: 60', self)
        self.layout.addWidget(self.label)

        self.bpmSlider = QSlider(Qt.Horizontal, self)
        self.bpmSlider.setMinimum(40)
        self.bpmSlider.setMaximum(208)
        self.bpmSlider.setValue(60)
        self.bpmSlider.valueChanged.connect(self.updateBPM)
        self.layout.addWidget(self.bpmSlider)

        self.toggleButton = QPushButton('Start', self)
        self.toggleButton.clicked.connect(self.toggleMetronome)
        self.layout.addWidget(self.toggleButton)

        self.worker = MetronomeWorker(60)
        self.worker.tick.connect(self.tick)

        self.player = QMediaPlayer()
        tickPath = Path(__file__).parent / "tick.mp3"
        #tickPath = "E:/lollms/discussion_databases/default/77/tick.mp3"
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(str(tickPath))))
        self.isRunning = False

        self.setLayout(self.layout)

    def updateBPM(self):
        self.label.setText(f'BPM: {self.bpmSlider.value()}')
        if self.isRunning:
            self.worker.stop()
            self.worker = MetronomeWorker(self.bpmSlider.value())
            self.worker.start()

    def toggleMetronome(self):
        if self.isRunning:
            self.worker.stop()
            self.toggleButton.setText('Start')
            self.isRunning = False
        else:
            self.worker = MetronomeWorker(self.bpmSlider.value())
            self.worker.start()
            self.worker.tick.connect(self.tick)
            self.toggleButton.setText('Stop')
            self.isRunning = True

    def tick(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.stop()
        self.player.play()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MetronomeApp()
    ex.show()
    sys.exit(app.exec_())

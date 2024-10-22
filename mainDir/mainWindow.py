import logging

from mainDir.widgets.menuWidget.mainMenu import MenuWidget

# Clear any existing handlers
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from PyQt6.QtCore import pyqtSignal, QTimer
from PyQt6.QtWidgets import *
import tracemalloc
import matplotlib.pyplot as plt


from mainDir.outputDevice.recording.RecordingWidget014 import RecordingWidget014
from mainDir.outputDevice.streaming.streamingWidget016 import StreamingWidget016
from mainDir.outputs.openGLViewerThread016 import OpenGLViewerThread016
from mainDir.mixEffect.mixEffects017 import MixEffect017


class MainWindow(QMainWindow):
    new_SIGNAL = pyqtSignal()
    newAndLoad_SIGNAL = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        #tracemalloc.start()  # Start memory tracking
        self.fps_values = []  # List to store FPS values over time
        self.memory_usage = []  # List to store memory usage over time

        # Creazione di MixEffect in un thread separato
        self.mixEffect_1 = MixEffect017()
        self.fpsLabel = QLabel("FPS: N/A", self)
        self.previewViewer = OpenGLViewerThread016()
        self.cleanFeedViewer = OpenGLViewerThread016()
        self.externalViewer = OpenGLViewerThread016()
        self.menu_widget = MenuWidget(self.mixEffect_1, self)
        self.signal_Clock = QTimer()
        self.initUI()
        self.initGeometry()
        self.initMenu()
        self.initStatusBar()
        self.initConnections()
        self.externalViewer.show()
        self.recordingWidget = RecordingWidget014(self.cleanFeedViewer)
        self.recordingWidget.showWin()
        self.streamWidget = StreamingWidget016(self.cleanFeedViewer)
        self.streamWidget.showWin()

        self.signal_Clock.timeout.connect(self.updateOutput)
        self.signal_Clock.start(12)

    def closeEvent(self, event, *args, **kwargs):
        # Ferma tutti i thread in MixEffect prima di chiudere
        self.mixEffect_1.close()  # Assicurati che MixEffect chiuda i thread
        # Chiudi i viewer esterni e widget
        self.externalViewer.close()
        # to do: check properly Closing of streamWidget and recordingWidget
        self.recordingWidget.close()
        self.streamWidget.close()
        # Mostra metriche di performance
        self.display_performance_metrics()
        event.accept()

    def initUI(self):
        centralWidget = QWidget()
        mainLayout = QVBoxLayout()
        viewerLayout = QHBoxLayout()
        viewerLayout.addWidget(self.previewViewer)
        viewerLayout.addWidget(self.cleanFeedViewer)
        mainLayout.addLayout(viewerLayout)
        mainLayout.addWidget(self.fpsLabel)
        mainLayout.addWidget(self.mixEffect_1)
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

    def initGeometry(self):
        self.setGeometry(100, 100, 1300, 800)
        self.previewViewer.setFixedSize(640, 360)
        self.cleanFeedViewer.setFixedSize(640, 360)
        self.setWindowTitle("Main Window")

    def initStyle(self):
        pass

    def initConnections(self):
        pass


    def updateOutput(self):
        prw_frame, prg_frame, fps = self.mixEffect_1.getMixed()
        self.previewViewer.setFrame(prw_frame)
        self.cleanFeedViewer.setFrame(prg_frame)
        self.externalViewer.setQImage(self.cleanFeedViewer.getQImage())
        self.fpsLabel.setText(f"FPS: {fps:.2f}")
        # Collect performance data
        self.fps_values.append(fps)
        current, peak = tracemalloc.get_traced_memory()
        self.memory_usage.append(current / 10 ** 6)  # Convert to MB

    def display_performance_metrics(self):
        average_fps = sum(self.fps_values) / len(self.fps_values)
        print(f"Average FPS: {average_fps:.2f}")
        print(f"Memory usage peak: {max(self.memory_usage):.2f} MB")

        plt.figure(figsize=(10, 5))
        plt.subplot(1, 2, 1)
        plt.plot(self.fps_values, label="FPS over time")
        plt.axhline(y=average_fps, color="r", linestyle="--", label=f"Avg FPS: {average_fps:.2f}")
        plt.xlabel("Time (frames)")
        plt.ylabel("FPS")
        plt.legend()

        plt.subplot(1, 2, 2)
        plt.plot(self.memory_usage, label="Memory Usage (MB)")
        plt.xlabel("Time (frames)")
        plt.ylabel("Memory (MB)")
        plt.legend()

        plt.tight_layout()
        plt.show()

    def initMenu(self):
        self.setMenuBar(self.menu_widget)

    def initStatusBar(self):
        self.statusBar().showMessage("Ready")

    def setMainOutFullscreen(self):
        self.externalViewer.showFullScreen()

    def deserialize(self, data):
        self.mixEffect_1.deserialize(data)


if __name__ == "__main__":
    app = QApplication([])
    win = MainWindow()
    win.show()
    app.exec()

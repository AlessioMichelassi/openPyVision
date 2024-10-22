from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

from mainDir.inputDevice.generatorDevice.inputDevice_colorGenerator import InputDevice_ColorGenerator
from mainDir.inputDevice.generatorDevice.inputDevice_noiseGenerator import InputDevice_NoiseGenerator
from mainDir.videoHub.videoHubData018 import VideoHubData018
from mainDir.outputs.openGLViewer015 import OpenGLViewer015


class VideoHubDataTester(QWidget):

    def __init__(self, videoHub, inputPosition):
        super().__init__()
        self.viewer = OpenGLViewer015()
        self.fpsLabel = QLabel("FPS: 0.00")
        self.videoHub = videoHub
        self.inputPosition = inputPosition
        self.inputDevice = self.videoHub.getInputDevice(self.inputPosition)

        if self.inputDevice is None:
            raise ValueError(f"Errore: Nessun dispositivo di input trovato alla posizione {self.inputPosition}")

        self.graphicInterface = self.inputDevice.graphicInterface
        self.btnActivate = QPushButton("Activate")
        self.timerInterface = QTimer(self)
        self.timerInterface.timeout.connect(self.updateInterface)
        self.initUI()
        self.initConnections()
        self.initGeometry()

    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.viewer)
        main_layout.addWidget(self.fpsLabel)
        widget_layout = QHBoxLayout()
        widget_layout.addWidget(self.graphicInterface)
        widget_layout.addWidget(self.btnActivate)
        main_layout.addLayout(widget_layout)
        self.setLayout(main_layout)

    def initConnections(self):
        self.btnActivate.clicked.connect(self.startDevice)
        self.inputDevice.graphicInterface.typeChanged.connect(self.onTypeChanged)

    def initGeometry(self):
        self.viewer.setMinimumSize(640, 480)
        self.btnActivate.setCheckable(True)
        self.btnActivate.setChecked(False)

    def updateInterface(self):
        frame = self.inputDevice.getFrame()
        fps = self.inputDevice.getFps()
        self.fpsLabel.setText(f"FPS: {fps:.2f}")
        self.viewer.setFrame(frame)

    def onTypeChanged(self, data):
        self.inputDevice.stop()
        self.btnActivate.setChecked(False)

    def startDevice(self):
        if self.btnActivate.isChecked():
            self.timerInterface.start(1000 // 65)
            self.videoHub.startInputDevice(self.inputPosition)
        else:
            self.timerInterface.stop()
            self.videoHub.stopInputDevice(self.inputPosition)


if __name__ == "__main__":
    app = QApplication([])

    # Creazione di VideoHubData e aggiunta di dispositivi di input
    videoHub = VideoHubData018()
    videoHub.addInputDevice(1, InputDevice_NoiseGenerator("Noise Generator"))
    videoHub.addInputDevice(2, InputDevice_ColorGenerator("Color Generator"))

    # Test di VideoHubData alla posizione 1 (Noise Generator)
    tester = VideoHubDataTester(videoHub, 1)  # Puoi anche cambiare la posizione per testare altri input
    tester.show()
    app.exec()

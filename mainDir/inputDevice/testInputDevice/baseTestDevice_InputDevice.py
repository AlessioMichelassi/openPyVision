"""
Questa classe deve testare l'inputDevice.
Ogni inputDevice è composta da:
    - un inputObject
    - un thread
    - una graphic Interface



"""
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *


from mainDir.outputs.openGLViewer015 import OpenGLViewer015


class InputDeviceAppTester(QWidget):

    def __init__(self, inputDevice):
        super().__init__()
        self.viewer = OpenGLViewer015()
        self.fpsLabel = QLabel("FPS: 0.00")
        self.inputDevice = inputDevice
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
            self.inputDevice.start()
        else:
            self.timerInterface.stop()
            self.inputDevice.stop()

if __name__ == "__main__":
    app = QApplication([])
    from mainDir.inputDevice.generatorDevice.inputDevice_noiseGenerator import InputDevice_NoiseGenerator
    tester = InputDeviceAppTester(InputDevice_NoiseGenerator("Noise Generator"))
    tester.show()
    app.exec()
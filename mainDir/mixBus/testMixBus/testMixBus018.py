import cv2
import numpy as np
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from mainDir.inputDevice.generatorDevice.inputDevice_noiseGenerator import InputDevice_NoiseGenerator
from mainDir.mixBus.mixBus018 import MixBus018, MIX_TYPE
from mainDir.videoHub.videoHubData018 import VideoHubData018


class TestMixBus18(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.input1 = InputDevice_NoiseGenerator("1")
        self.input2 = InputDevice_NoiseGenerator("2")
        self.videoHubData = VideoHubData018(self)
        self.videoHubData.addInputDevice(1, self.input1)
        self.videoHubData.addInputDevice(2, self.input2)

        self.videoHubData.startInputDevice(1)
        self.videoHubData.startInputDevice(2)
        self.mixBus = MixBus018(self.videoHubData)

        self.lblPreview = QLabel()
        self.lblProgram = QLabel()
        self.btnCut = QPushButton("CUT")
        self.btnAutoMix = QPushButton("AutoMix")
        self.sldFade = QSlider()
        self.cmbEffect = QComboBox()
        self.cmbEffect.addItems(["Fade", "Wipe Left to Right", "Wipe Right to Left"])
        self.sldFade.setOrientation(Qt.Orientation.Horizontal)
        self.sldFade.setRange(0, 100)
        self.initUI()
        self.initGeometry()
        self.initConnections()
        # Start a timer to call getMixed periodically
        self.timer = QTimer()
        self.timer.timeout.connect(self.mixBus.getMixed)
        self.timer.start(1000 // 60)

    def initUI(self):
        mainLayout = QVBoxLayout()
        viewerLayout = QHBoxLayout()
        viewerLayout.addWidget(self.lblPreview)
        viewerLayout.addWidget(self.lblProgram)
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        buttonLayout = QHBoxLayout()
        buttonLayout.addItem(spacer)
        buttonLayout.addWidget(self.btnCut)
        buttonLayout.addWidget(self.btnAutoMix)
        buttonLayout.addWidget(self.sldFade)
        buttonLayout.addWidget(self.cmbEffect)
        mainLayout.addLayout(viewerLayout)
        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)

    def initGeometry(self):
        self.lblPreview.setFixedSize(640, 360)
        self.lblProgram.setFixedSize(640, 360)

    def initConnections(self):
        self.mixBus.frame_ready.connect(self.updateFrame)
        self.btnCut.clicked.connect(self.cut)
        self.btnAutoMix.clicked.connect(self.autoMix)
        self.sldFade.valueChanged.connect(self.setFade)
        self.cmbEffect.currentIndexChanged.connect(self.setEffect)

    @pyqtSlot(np.ndarray, np.ndarray, float)
    def updateFrame(self, prw_frame, prg_frame, fps):
        # Convert frames to QImage and display
        if prw_frame is not None:
            prw_frame = cv2.resize(prw_frame, (640, 360))
            prw_frame = cv2.cvtColor(prw_frame, cv2.COLOR_BGR2RGB)
            prw_image = QImage(prw_frame.data, prw_frame.shape[1], prw_frame.shape[0], QImage.Format.Format_RGB888)
            self.lblPreview.setPixmap(QPixmap.fromImage(prw_image))
        else:
            self.lblPreview.clear()

        if prg_frame is not None:
            prg_frame = cv2.resize(prg_frame, (640, 360))
            prg_frame = cv2.cvtColor(prg_frame, cv2.COLOR_BGR2RGB)
            prg_image = QImage(prg_frame.data, prg_frame.shape[1], prg_frame.shape[0], QImage.Format.Format_RGB888)
            self.lblProgram.setPixmap(QPixmap.fromImage(prg_image))
        else:
            self.lblProgram.clear()

    def cut(self):
        self.mixBus.cut()

    def autoMix(self):
        self.mixBus.autoMix()

    def setFade(self, value):
        self.mixBus.setFade(value)

    def setEffect(self, index):
        effect = self.cmbEffect.currentText()
        if effect == "Fade":
            self.mixBus.setEffectType(MIX_TYPE.FADE)
        elif effect == "Wipe Left to Right":
            self.mixBus.setEffectType(MIX_TYPE.WIPE_LEFT_TO_RIGHT)
        elif effect == "Wipe Right to Left":
            self.mixBus.setEffectType(MIX_TYPE.WIPE_RIGHT_TO_LEFT)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    test = TestMixBus18()
    test.show()
    sys.exit(app.exec())

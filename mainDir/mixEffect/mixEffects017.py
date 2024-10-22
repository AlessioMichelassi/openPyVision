from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
import sys

from mainDir.MrKeyboard.mixingKeyboard import MixerKeyboard
from mainDir.mixBus.mixBus017 import MixBus017_NoThread
from mainDir.outputs.openGLViewerThread016 import OpenGLViewerThread016
from mainDir.tallyManager.tallyManager import TallyManager
from mainDir.videoHub.videoHubWidget.videoHubWidget019 import VideoHubWidget019
from mainDir.videoHub.videoHubData018 import VideoHubData018


class MixEffect017(QWidget):
    prwViewer = None
    prgViewer = None
    mainOut = None
    fpsLabel = None
    time_interval = 12 # teorically 1000/60 = 16.67 but we need to consider the time to process the frame

    def __init__(self, isTestModality=False, parent=None):
        super().__init__(parent)
        self.mrKeyboard = MixerKeyboard(self)
        self.tallyManager = TallyManager(self)
        self.videoHubData = VideoHubData018(self)
        self.videoHubWidget = VideoHubWidget019(self.videoHubData)
        self.mixEffectTimer = QTimer(self)
        # Initialize MixBus
        self.mixBus = MixBus017_NoThread(self.videoHubData)
        # with test Modality you have
        # two monitors loaded within the interface
        self.isTestModality = isTestModality
        self.initUI()
        self.initConnections()
        self.initGeometry()

    def closeEvent(self, event, *args, **kwargs):
        event.accept()

    def initUI(self):
        mainLayout = QVBoxLayout()
        if self.isTestModality:
            self.fpsLabel = QLabel("FPS: N/A", self)
            self.prwViewer = OpenGLViewerThread016()
            self.prgViewer = OpenGLViewerThread016()
            self.mainOut = OpenGLViewerThread016()
            self.mainOut.setFixedSize(1280, 720)
            self.mainOut.show()
            viewer_layout = QHBoxLayout()
            viewer_layout.addWidget(self.prwViewer)
            viewer_layout.addWidget(self.prgViewer)
            mainLayout.addLayout(viewer_layout)
            self.mixEffectTimer.timeout.connect(self.getMixed)
            self.mixEffectTimer.start(self.time_interval)
        central_layout = QHBoxLayout()
        central_layout.addWidget(self.videoHubWidget)
        keyboard_Layout = QVBoxLayout()
        keyboard_Layout.addSpacing(100)
        keyboard_Layout.addWidget(self.mrKeyboard)
        central_layout.addLayout(keyboard_Layout)
        mainLayout.addLayout(central_layout)
        self.setLayout(mainLayout)

    def initConnections(self):
        self.videoHubData.tally_SIGNAL.connect(self.tallyManager.parseTallySignal)
        self.mrKeyboard.tally_SIGNAL.connect(self.tallyManager.parseTallySignal)
        self.tallyManager.mixBus_SIGNAL.connect(self.mixBus.parseTallySignal)
        self.tallyManager.keyboard_SIGNAL.connect(self.mrKeyboard.parseTallySignal)
        print("Connected tally_SIGNAL to onVideoHubTallySignal")

    def getMixed(self):
        prw_frame, prg_frame = self.mixBus.getMixed()
        fps = self.mixBus.getFps()
        if self.isTestModality:
            self.prwViewer.setFrame(prw_frame)
            self.prgViewer.setFrame(prg_frame)
            self.mainOut.setQImage(self.prgViewer.getQImage())
            self.fpsLabel.setText(f"FPS: {fps:.2f}")
        return prw_frame, prg_frame, fps

    def initGeometry(self):
        self.videoHubWidget.setMaximumWidth(1200)
        if self.isTestModality:
            self.prwViewer.setFixedSize(640, 360)
            self.prgViewer.setFixedSize(640, 360)

    def onVideoHubTallySignal(self, tally_data):
        print(f"MixEffect Received tally signal: {tally_data}")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    testWindow = MixEffect017(True)
    testWindow.show()
    sys.exit(app.exec())

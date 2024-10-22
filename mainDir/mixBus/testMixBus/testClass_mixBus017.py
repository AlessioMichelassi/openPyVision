import json
import sys
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from mainDir.inputDevice.generatorDevice.inputDevice_colorGenerator import InputDevice_ColorGenerator
from mainDir.inputDevice.generatorDevice.inputDevice_noiseGenerator import InputDevice_NoiseGenerator
from mainDir.inputDevice.systemWidget.inputDevice_stingerPlayer import InputDevice_StingerAnimation
from mainDir.inputDevice.systemWidget.inputObject.inputObject_StingerPlayer import InputObject_StingerPlayerForMixBus
from mainDir.inputDevice.systemWidget.threadLoader.stingerLoaderV04T import StingerLoaderV04T
from mainDir.mixBus.mixBus017 import MIX_TYPE, MixBus017_NoThread
from mainDir.outputs.openGLViewer015 import OpenGLViewer015
from mainDir.videoHub.videoHubData018 import VideoHubData018


class testMixBus017(QWidget):

    tally_SIGNAL = pyqtSignal(dict, name="tallySignal")
    def __init__(self, parent=None):
        super().__init__(parent)

        # Init external widgets
        self.videoHub = VideoHubData018()
        # Inizializzazione MixBus
        self.mixBus = MixBus017_NoThread(self.videoHub)

        # Init internal widgets
        self.prw_image = QImage()
        self.prg_image = QImage()
        self.previewViewer = OpenGLViewer015()
        self.programViewer = OpenGLViewer015()
        self.btnCut = QPushButton("CUT")
        self.btnAutoMix = QPushButton("AutoMix")
        self.sldFade = QSlider()
        self.cmbEffect = QComboBox(self)
        self.lblFrameRate = QLabel("Frame Rate: 0.0")

        # Init UI
        self.initUI()
        self.initGeometry()
        self.initConnections()
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateFrame)
        self.timer.start(1000 // 60)

    def initUI(self):
        """
        This function initializes the UI.
        """
        main_layout = QVBoxLayout()
        viewerLayout = QHBoxLayout()
        viewerLayout.addWidget(self.previewViewer)
        viewerLayout.addWidget(self.programViewer)
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        buttonLayout = QHBoxLayout()
        buttonLayout.addItem(spacer)
        buttonLayout.addWidget(self.btnCut)
        buttonLayout.addWidget(self.btnAutoMix)
        buttonLayout.addWidget(self.sldFade)
        buttonLayout.addWidget(self.cmbEffect)
        main_layout.addLayout(viewerLayout)
        main_layout.addLayout(buttonLayout)
        main_layout.addWidget(self.lblFrameRate)
        self.setLayout(main_layout)

    def initGeometry(self):
        """
        Initialize the geometry and UI component sizes.
        """
        self.previewViewer.setFixedSize(640, 360)
        self.programViewer.setFixedSize(640, 360)
        self.cmbEffect.addItems([
            "Fade", "Wipe Left to Right", "Wipe Right to Left",
            "Wipe Top to Bottom", "Wipe Bottom to Top", "Stinger", "Still"
        ])
        self.sldFade.setOrientation(Qt.Orientation.Horizontal)
        self.sldFade.setRange(0, 100)

    def initConnections(self):
        """
        Setup signal-slot connections.
        """
        self.btnCut.clicked.connect(self.cut)
        self.btnAutoMix.clicked.connect(self.autoMix)
        self.sldFade.valueChanged.connect(self.setFade)
        self.cmbEffect.currentIndexChanged.connect(self.setEffect)

    def updateFrame(self):
        """
        Update the preview and program frames in the UI and show the current frame rate.
        """
        prw_frame, prg_frame = self.mixBus.getMixed()
        self.lblFrameRate.setText(f"Frame Rate: {self.mixBus.getFps():.2f}")
        self.prw_image = QImage(prw_frame.data, prw_frame.shape[1], prw_frame.shape[0], QImage.Format.Format_BGR888)
        self.prg_image = QImage(prg_frame.data, prg_frame.shape[1], prg_frame.shape[0], QImage.Format.Format_BGR888)
        self.previewViewer.setFrame(prw_frame)
        self.programViewer.setFrame(prg_frame)

    def cut(self):
        """
        Handle the 'CUT' button click.
        """
        self.mixBus.cut()

    def autoMix(self):
        """
        Handle the 'AutoMix' button click.
        """
        self.mixBus.autoMix()

    def setFade(self):
        """
        Update the fade value in the MixBus when the slider changes.
        """
        self.mixBus.setFade(self.sldFade.value())

    def setEffect(self):
        """
        Update the effect type in the MixBus based on the selected value from the combo box.
        """
        effect = self.cmbEffect.currentText()
        if effect == "Fade":
            self.mixBus.setEffectType(MIX_TYPE.FADE)
        elif effect == "Wipe Left to Right":
            self.mixBus.setEffectType(MIX_TYPE.WIPE_LEFT_TO_RIGHT)
        elif effect == "Wipe Right to Left":
            self.mixBus.setEffectType(MIX_TYPE.WIPE_RIGHT_TO_LEFT)
        elif effect == "Wipe Top to Bottom":
            self.mixBus.setEffectType(MIX_TYPE.WIPE_TOP_TO_BOTTOM)
        elif effect == "Wipe Bottom to Top":
            self.mixBus.setEffectType(MIX_TYPE.WIPE_BOTTOM_TO_TOP)
        elif effect == "Stinger":
            self.mixBus.setEffectType(MIX_TYPE.WIPE_STINGER)
            cmd = {'sender': 'tallyManager', 'cmd': 'auto', 'preview': '2', 'program': '1', 'effect': 'Wipe Stinger', 'fade': 0.0}

            self.mixBus.parseTallySignal(cmd)
        elif effect == "Still":
            self.mixBus.setEffectType(MIX_TYPE.FADE_STILL)

    def emitTallySignal(self, cmd, position):
        tally_status = {
            'sender': 'videoHub',
            'cmd': cmd,
            'position': position,
        }
        print(f"Emitting tally signal: {tally_status}")
        self.tally_SIGNAL.emit(tally_status)


    def parseTallySignal(self, data):
        """
        This function parses the tally signal and performs the action accordingly.
        """
        cmd = data['cmd']
        position = data['position']

        if cmd == 'cut':
            self.mixBus.cut()
        elif cmd == 'auto':
            self.mixBus.autoMix()
        elif cmd == 'faderChange':
            self.mixBus.setFade(position)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    test = testMixBus017()
    test.show()

    # Aggiunta e avvio degli input devices
    print("Aggiunta di dispositivi di input...")
    input1 = InputDevice_ColorGenerator("Color Generator")
    test.videoHub.addInputDevice(1, input1)
    input2 = InputDevice_NoiseGenerator("Noise Generator")
    test.videoHub.addInputDevice(2, input2)
    print("Dispositivi di input aggiunti.")
    print(json.dumps(test.videoHub.serialize(), indent=4))

    print("Avvio dei dispositivi di input...")
    test.videoHub.startInputDevice(1)
    test.videoHub.startInputDevice(2)

    # Debug per verificare lo stato degli input
    prw_input = test.videoHub.getInputDevice(1)
    prg_input = test.videoHub.getInputDevice(2)
    if prw_input is None:
        print("Errore: Dispositivo di input 1 non trovato o non avviato correttamente.")
    else:
        print(f"Dispositivo di input 1: {prw_input}")

    if prg_input is None:
        print("Errore: Dispositivo di input 2 non trovato o non avviato correttamente.")
    else:
        print(f"Dispositivo di input 2: {prg_input}")
    tally_status = {
        'sender': 'videoHub',
        'cmd': 'inputChanged',
        'position': 1,
    }
    test.mixBus.parseTallySignal(tally_status)
    tally_status = {
        'sender': 'videoHub',
        'cmd': 'inputChanged',
        'position': 2,
    }
    test.mixBus.parseTallySignal(tally_status)
    def onStingerLoaded():
        print("Stinger loaded.")
        stingerDevice = InputDevice_StingerAnimation("Stinger Animation")
        global stingerLoader
        inputObject = InputObject_StingerPlayerForMixBus(None, 0)
        inputObject.setStingerPremultipliedImages(
            stingerLoader.stingerPreMultipliedImages)
        inputObject.setStingerInvAlphaImages(
            stingerLoader.stingerInvAlphaImages)
        stingerDevice.setInputObject(inputObject)
        test.videoHub.addStingerPlayer(0, stingerDevice)
        test.videoHub.startStingerPlayer(0)
        tally_status = {
            'sender': 'videoHub',
            'cmd': 'stingerReady',
            'position': 0,
        }
        test.mixBus.parseTallySignal(tally_status)

    path = r"/mainDir/imgs/testSequence"
    stingerLoader = StingerLoaderV04T(path)
    stingerLoader.stingerReady.connect(onStingerLoaded)
    stingerLoader.start()



    sys.exit(app.exec())



import time
import numpy as np
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from mainDir.outputs.openGLViewer015 import OpenGLViewer015


class VideoAppExtended(QApplication):

    
    def __init__(self, argv, input_object):
        super().__init__(argv)
        # Usa l'input passato invece di creare uno specifico
        self.input1 = input_object
        # Inizializza i widget interni
        self.widget = QWidget()
        self.viewer = OpenGLViewer015()
        self.fpsLabel = QLabel("FPS: 0.00")
        self.displayLabel = QLabel()
        self.uiTimer = QTimer(self)
        self.uiTimer.start(10)  # Update UI a circa 65 FPS
        self.btnApplyClahe = QPushButton("Apply CLAHE")
        self.btnApplyHistogramEqualization = QPushButton("Apply Histogram Equalization")
        self.btnApplyGammaCorrection = QPushButton("Apply Gamma Correction")
        self.btnApplyInvert = QPushButton("invert")
        self.qImage = QImage()
        # Inizializza l'interfaccia
        self.initUI()
        self.initConnections()
        self.initGeometry()

    
    def __del__(self):
        self.stop_app()

    
    def initUI(self):
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.viewer)
        mainLayout.addWidget(self.fpsLabel)
        mainLayout.addWidget(self.displayLabel)
        buttonLayout = self.initButtonLayout()
        mainLayout.addLayout(buttonLayout)
        self.widget.setLayout(mainLayout)


    def initButtonLayout(self):
        self.initButton(self.btnApplyClahe, self.setClahe)
        self.initButton(self.btnApplyHistogramEqualization, self.setHistogramEqualization)
        self.initButton(self.btnApplyGammaCorrection, self.setGammaCorrection)
        self.initButton(self.btnApplyInvert, self.setInvert)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.btnApplyClahe)
        buttonLayout.addWidget(self.btnApplyHistogramEqualization)
        buttonLayout.addWidget(self.btnApplyGammaCorrection)
        buttonLayout.addWidget(self.btnApplyInvert)
        return buttonLayout

    
    def initButton(self, button, function):
        button.setCheckable(True)
        button.setChecked(False)
        button.clicked.connect(function)

    
    def initConnections(self):
        self.uiTimer.timeout.connect(self.display_frame)

    
    def initGeometry(self):
        self.viewer.setFixedSize(1920, 1080)
        self.widget.setGeometry(10, 50, 1920, 1080)
        self.widget.show()

    def display_frame(self):
        self.input1.captureFrame()
        frame = self.input1.getFrame()
        if frame is not None and frame.size != 0:
            display_start_time = time.time()
            self.viewer.setFrame(frame)
            display_time = time.time() - display_start_time
            self.displayLabel.setText(f"Frame displayed in {display_time:.6f} seconds")
            self.fpsLabel.setText(f"FPS: {self.input1.fps:.2f}")

    
    def stop_app(self):
        print(f"Media FPS: {self.input1.fps:.2f}")
        self.exit()

    
    def setClahe(self, value):
        self.input1.isFrameClahe = value

    
    def setHistogramEqualization(self, value):
        self.input1.isFrameHistogramEqualizationYUV = value

    
    def setGammaCorrection(self,value):
        self.input1.isFrameGammaCorrection = value

    
    def setInvert(self, value):
        self.input1.isFrameInverted = value

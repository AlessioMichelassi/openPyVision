import logging

import cv2
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtOpenGLWidgets import QOpenGLWidget

from mainDir.errorClass.loggerClass import ErrorClass


class OpenGLViewer(QOpenGLWidget):

    @ErrorClass().log(log_level=logging.INFO)
    def __init__(self, resolution: QSize = QSize(640, 360), parent=None):
        super().__init__(parent)
        self.image = QImage()
        self.resolution = resolution

    @ErrorClass().log(log_level=logging.INFO)
    def setImage(self, image):
        # fra il resize e l'update, l'immagine viene ridimensionata
        self.image = image
        self.update()

    @ErrorClass().log(log_level=logging.INFO)
    def paintGL(self):
        if not self.image is None:
            painter = QPainter(self)
            painter.drawImage(self.rect(), self.image)
            painter.end()

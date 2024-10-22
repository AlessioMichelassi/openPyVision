import sys

import cv2
import numpy as np
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from mainDir.inputDevice.systemWidget.inputDevice_stingerPlayer import InputDevice_StingerAnimation


class TestStingerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.index = 0
        # Creazione del dispositivo stinger
        self.inputDevice = InputDevice_StingerAnimation("Stinger Animation Device")

        # Layout per i viewer
        self.layout = QVBoxLayout(self)

        # Creazione di tre QLabel per visualizzare i frame
        self.viewer1 = QLabel(self)
        self.viewer1.setFixedSize(640, 360)
        self.viewer2 = QLabel(self)
        self.viewer2.setFixedSize(640, 360)
        self.viewer3 = QLabel(self)
        self.viewer3.setFixedSize(640, 360)
        self.layout.addWidget(QLabel("Premultiplied Frame"))
        self.layout.addWidget(self.viewer1)
        self.layout.addWidget(QLabel("Inverse Alpha Frame"))
        self.layout.addWidget(self.viewer2)
        self.layout.addWidget(QLabel("Custom Frame"))
        self.layout.addWidget(self.viewer3)

        # Collegamento del segnale stingerLoaded al caricamento delle immagini
        self.inputDevice.graphicInterface.stingerLoaded.connect(self.onStingerLoaded)

        # Avvio del caricamento delle immagini con il widget
        self.inputDevice.graphicInterface.show()

        # Timer per aggiornare i viewer ogni 30 FPS
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_viewers)

    def onStingerLoaded(self):
        """
        Funzione invocata quando lo stinger è caricato e pronto.
        Avvia il timer per la visualizzazione delle immagini.
        """
        self.timer.start(1000 // 60)  # 30 FPS

    def update_viewers(self):
        """
        Aggiorna i viewer con i frame correnti dello stinger.
        """
        self.inputDevice.setIndex(self.index)
        premultiplied_frame, inv_alpha_frame = self.inputDevice.getFrames()
        # Converti i frame OpenCV in QPixmap e mostralo sui viewer
        pixmap1 = self.convert_cv_to_pixmap(premultiplied_frame)
        pixmap2 = self.convert_cv_to_pixmap(inv_alpha_frame)
        random = np.random.randint(0, 255, (1080, 1920, 3), np.uint8)
        mixed = cv2.multiply(inv_alpha_frame, random, dtype=cv2.CV_8U)
        frame = cv2.add(mixed, premultiplied_frame)
        pixmap3 = self.convert_cv_to_pixmap(frame)  # O un'altra combinazione, personalizza qui

        self.viewer1.setPixmap(pixmap1.scaled(self.viewer1.size()))
        self.viewer2.setPixmap(pixmap2.scaled(self.viewer2.size()))
        self.viewer3.setPixmap(pixmap3.scaled(self.viewer3.size()))
        if self.index < self.inputDevice.getLength()-1:
            self.index += 1
        else:
            self.index = 0

    @staticmethod
    def convert_cv_to_pixmap(cv_img):
        if len(cv_img.shape) == 2:  # Immagine in scala di grigi
            height, width = cv_img.shape
            bytes_per_line = width
            q_img = QImage(cv_img.data, width, height, bytes_per_line, QImage.Format.Format_Grayscale8)
        else:  # Immagine RGB
            height, width, channel = cv_img.shape
            bytes_per_line = 3 * width
            q_img = QImage(cv_img.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        return QPixmap.fromImage(q_img)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Creazione della finestra di test
    window = TestStingerApp()
    window.show()

    sys.exit(app.exec())

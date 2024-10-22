# test class
import numpy as np
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
import cv2

from mainDir.inputDevice.systemWidget.threadLoader.stingerLoaderV04T import StingerLoaderV04T


class TestStingerLoaderV04T(QWidget):
    def __init__(self):
        super().__init__()
        self.index = 0
        path = r"C:\pythonCode\project\openPyVision\openPyVisionBook\openPyVision\mainDir\imgs\testSequence"
        self.stingerLoader = StingerLoaderV04T(path)
        self.stingerLoader.stingerReady.connect(self.onStingerLoaded)
        self.stingerLoader.progressUpdated.connect(self.onProgressUpdated)
        self.stingerLoader.start()

        self.layout = QVBoxLayout(self)
        self.viewer1 = QLabel(self)
        self.viewer2 = QLabel(self)
        self.viewer3 = QLabel(self)
        self.viewer1.setFixedSize(640,360)
        self.viewer2.setFixedSize(640,360)
        self.layout.addWidget(QLabel("Premultiplied Frame"))
        self.layout.addWidget(self.viewer1)
        self.layout.addWidget(QLabel("Inverse Alpha Frame"))
        self.layout.addWidget(self.viewer2)
        self.layout.addWidget(QLabel("Mixed Frame"))
        self.layout.addWidget(self.viewer3)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_viewers)

    def onStingerLoaded(self):
        self.timer.start(1000 // 30)

    def onProgressUpdated(self, progress):
        print(f"Loading progress: {progress}%")

    def update_viewers(self):
        self.stingerLoader.stop()
        premultiplied_frame = self.stingerLoader.stingerPreMultipliedImages[self.index]
        inv_alpha_frame = self.stingerLoader.stingerInvAlphaImages[self.index]
        self.index = (self.index + 1) % len(self.stingerLoader.stingerPreMultipliedImages)

        # Converti i frame OpenCV in QPixmap e mostralo sui viewer
        pixmap1 = self.convert_cv_to_pixmap(premultiplied_frame)

        # Scala i valori di `inv_alpha_frame` per visualizzarli correttamente
        inv_alpha_frame_visual = (inv_alpha_frame * 255).astype(np.uint8)
        pixmap2 = self.convert_cv_to_pixmap(inv_alpha_frame_visual)

        # Mostra i frame premoltiplicati e inv_alpha
        self.viewer1.setPixmap(pixmap1)
        self.viewer2.setPixmap(pixmap2)

        # Creazione di un'immagine di rumore e calcolo del frame mixato
        noise = np.random.randint(0, 255, (premultiplied_frame.shape[0], premultiplied_frame.shape[1], 3),
                                  dtype=np.uint8)
        mixed = cv2.multiply(inv_alpha_frame, noise.astype(np.float32) / 255.0, dtype=cv2.CV_32F)
        frame = cv2.add(mixed, premultiplied_frame.astype(np.float32))
        frame = np.clip(frame, 0, 255).astype(np.uint8)

        pixmap3 = self.convert_cv_to_pixmap(frame)
        self.viewer3.setPixmap(pixmap3)

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


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    test = TestStingerLoaderV04T()
    test.show()
    sys.exit(app.exec())
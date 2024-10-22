import logging
import sys
import cv2
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QCheckBox
from PyQt6.QtGui import QFont, QPixmap, QImage
from mainDir.errorClass.loggerClass import error_logger
from mainDir.inputDevice.systemWidget.inputDevice_stingerPlayer import InputDevice_StingerAnimation
from mainDir.videoHub.videoHubData018 import VideoHubData018

class TabWidget_StingerPlayer(QWidget):

    @error_logger.log(log_level=logging.INFO)
    def __init__(self, videoHub, start, end, parent=None, test_mode=False):
        super().__init__(parent)
        self.videoHubData = videoHub
        self.layout = QGridLayout(self)
        self.stingerPlayers = []
        self.active_checkboxes = []
        self.start = start
        self.end = end
        self.test_mode = test_mode
        self.test_labels = []
        self.timers = []
        self.initUI()
        self.initConnections()

    @error_logger.log(log_level=logging.INFO)
    def initUI(self):
        """
        Initializes the user interface.
        Each row contains a label, the stinger player's graphic interface,
        a checkbox to activate/deactivate the stinger, and (in test mode) a QLabel to display the stinger frames.
        """
        for i in range(self.start, self.end + 1):
            label = QLabel(f"Input_{i}")
            label.setFont(QFont("Arial", 12, QFont.Weight.Bold))

            stingerPlayerDevice = InputDevice_StingerAnimation(str(i), self, stingerNumber=i - self.start)
            self.videoHubData.addStingerPlayer(i, stingerPlayerDevice)
            self.stingerPlayers.append(stingerPlayerDevice)

            checkbox = QCheckBox("Active")
            checkbox.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            checkbox.setChecked(False)
            checkbox.setProperty('input_index', i - self.start)
            self.active_checkboxes.append(checkbox)

            row = i - self.start
            self.layout.addWidget(label, row, 0)
            self.layout.addWidget(stingerPlayerDevice.graphicInterface, row, 1)
            self.layout.addWidget(checkbox, row, 2)

            if self.test_mode:
                test_label = QLabel(self)
                test_label.setFixedSize(320, 180)
                self.layout.addWidget(test_label, row, 3)
                self.test_labels.append(test_label)
                timer = QTimer(self)
                timer.setInterval(1000 // 30)  # 30 FPS
                timer.timeout.connect(lambda idx=i - self.start: self.updateTestLabel(idx))
                self.timers.append(timer)
            else:
                self.test_labels.append(None)
                self.timers.append(None)

    @error_logger.log(log_level=logging.DEBUG)
    def initConnections(self):
        for checkbox in self.active_checkboxes:
            checkbox.stateChanged.connect(self.toggleCapture)

    @error_logger.log(log_level=logging.INFO)
    def toggleCapture(self, state):
        sender = self.sender()
        input_index = sender.property('input_index')
        stingerPlayer = self.stingerPlayers[input_index]

        if state:
            logging.info(f"Activating stinger player at position {input_index}")
            self.videoHubData.addStingerPlayer(input_index, stingerPlayer)
            self.videoHubData.startStingerPlayer(input_index)
            if self.test_mode:
                if stingerPlayer._input_object is not None:
                    stingerPlayer._input_object.setIndex(0)
                else:
                    logging.error("Input object is None")
                self.timers[input_index].start()
        else:
            logging.info(f"Deactivating stinger player at position {input_index}")
            self.videoHubData.removeStingerPlayer(input_index)
            if self.test_mode:
                self.timers[input_index].stop()
                self.test_labels[input_index].clear()
        print(self.printVideoHubContent())

    @error_logger.log(log_level=logging.INFO)
    def updateTestLabel(self, index):
        stingerPlayer = self.stingerPlayers[index]
        test_label = self.test_labels[index]

        if stingerPlayer._input_object is not None:
            # Increment the stinger index
            current_index = stingerPlayer._input_object.index
            stingerPlayer._input_object.setIndex((current_index + 1) % stingerPlayer._input_object.getLength())

            # Get the current frame
            premultiplied_frame, _ = stingerPlayer.getFrames()

            # Check that the frame is not None
            if premultiplied_frame is not None:
                # Convert the frame to QPixmap and update the QLabel
                pixmap = self.convert_cv_to_pixmap(premultiplied_frame)
                test_label.setPixmap(pixmap.scaled(test_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
            else:
                logging.error("Premultiplied frame is None")
        else:
            logging.error("Input object is None")

    @staticmethod
    def convert_cv_to_pixmap(cv_img):
        if len(cv_img.shape) == 2:
            height, width = cv_img.shape
            bytes_per_line = width
            q_img = QImage(cv_img.data, width, height, bytes_per_line, QImage.Format.Format_Grayscale8)
        elif cv_img.shape[2] == 3:
            cv_img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
            height, width, channel = cv_img_rgb.shape
            bytes_per_line = 3 * width
            q_img = QImage(cv_img_rgb.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        elif cv_img.shape[2] == 4:
            cv_img_rgba = cv2.cvtColor(cv_img, cv2.COLOR_BGRA2RGBA)
            height, width, channel = cv_img_rgba.shape
            bytes_per_line = 4 * width
            q_img = QImage(cv_img_rgba.data, width, height, bytes_per_line, QImage.Format.Format_RGBA8888)
        else:
            raise ValueError("Unsupported image format")
        return QPixmap.fromImage(q_img)

    @error_logger.log(log_level=logging.INFO)
    def printVideoHubContent(self):
        returnString = "VideoHub content stinger:\n"
        for index, _input in self.videoHubData.videoHubMatrix.items():
            returnString += f"Input {index}: {_input}\n"
        return returnString

if __name__ == "__main__":
    app = QApplication(sys.argv)
    videoHubData = VideoHubData018()
    window = TabWidget_StingerPlayer(videoHubData, 1, 4, test_mode=True)
    window.show()
    sys.exit(app.exec())

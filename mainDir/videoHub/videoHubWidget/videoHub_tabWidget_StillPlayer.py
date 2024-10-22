import logging

from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from mainDir.errorClass.loggerClass import error_logger
from mainDir.inputDevice.playerDevice.inputDevice_stillImagePlayerGenerator import InputDevice_StillImagePlayer

from mainDir.videoHub.videoHubData018 import VideoHubData018


class TabWidget_StillPlayer(QWidget):

    @error_logger.log(log_level=logging.INFO)
    def __init__(self, videoHub, start, end, parent=None):
        super().__init__(parent)
        self.videoHubData = videoHub
        self.layout = QGridLayout(self)
        self.still_players = []
        self.stacked_widgets = []
        self.active_checkboxes = []
        self.start = start
        self.end = end
        self.initUI()
        self.initConnections()

    @error_logger.log(log_level=logging.INFO)
    def initUI(self):
        """
        Questa inizializza l'interfaccia grafica
        Ogni riga contiene una cmbBox per la selezione dell'input e
        una stackedWidget per inserire l'interfaccia grafica del l'input selezionato
        di solito si parte da 1 a 4 in modo da avere in numro dell'input corrispondete
        con input_1, input_2, input_3, input_4
        :return:
        """
        for i in range(self.start, self.end + 1):
            label = QLabel(f"Input_{i}")
            label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            stillPlayer = InputDevice_StillImagePlayer(str(i), self)
            self.videoHubData.addStillPlayer(i, stillPlayer)
            self.still_players.append(stillPlayer)
            checkbox = QCheckBox("Active")
            checkbox.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            checkbox.setChecked(False)
            self.active_checkboxes.append(checkbox)
            row = i - self.start
            self.layout.addWidget(label, row, 0)
            self.layout.addWidget(stillPlayer.graphicInterface, row, 1)
            self.layout.addWidget(checkbox, row, 2)
            # i widget così creati vengono inseriti in alcune liste per poterli cercare facilmente
            self.active_checkboxes.append(checkbox)

    @error_logger.log(log_level=logging.DEBUG)
    def initConnections(self):
        for checkbox, stillPlayer in zip(self.active_checkboxes, self.still_players):
            checkbox.stateChanged.connect(lambda state, sp=stillPlayer, cb=checkbox: self.toggleCapture(state, cb, sp))


    @error_logger.log(log_level=logging.INFO)
    def toggleCapture(self, state, checkbox, stillPlayer):
        sender = self.sender()
        input_index = self.active_checkboxes.index(checkbox)
        if state:
            self.videoHubData.startStillPlayer(input_index)
        else:
            self.videoHubData.stopStillPlayer(input_index)

    @error_logger.log(log_level=logging.INFO)
    def printVideoHubContent(self):
        returnString = "VideoHub content still:\n"
        for index, _input in self.videoHubData.videoHubMatrix.items():
            returnString += f"Input {index}: {_input}\n"
        return returnString


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    videoHubData = VideoHubData018()
    window = TabWidget_StillPlayer(videoHubData, 1, 4)
    window.show()
    sys.exit(app.exec())
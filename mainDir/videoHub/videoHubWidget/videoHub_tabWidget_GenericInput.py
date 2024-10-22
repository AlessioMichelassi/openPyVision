import logging

from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from mainDir.errorClass.loggerClass import error_logger
from mainDir.inputDevice.captureDevice.inputDevice_cameraCapture import InputDevice_CameraCapture
from mainDir.inputDevice.captureDevice.inputDevice_desktopCapture import InputDevice_DesktopCapture
from mainDir.inputDevice.generatorDevice.inputDevice_colorGenerator import InputDevice_ColorGenerator
from mainDir.inputDevice.generatorDevice.inputDevice_noiseGenerator import InputDevice_NoiseGenerator
from mainDir.inputDevice.generatorDevice.inputDevice_smpteGenerator import InputDevice_SmpteGenerator
from mainDir.inputDevice.playerDevice.inputDevice_stillImagePlayerGenerator import \
    InputDevice_StillImagePlayer
from mainDir.videoHub.videoHubData018 import VideoHubData018


class TabWidget_GenericInput(QWidget):

    @error_logger.log(log_level=logging.INFO)
    def __init__(self, videoHub, start, end, parent=None):
        super().__init__(parent)
        self.videoHubData = videoHub
        self.layout = QGridLayout(self)
        self.combo_boxes = []
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

            combo = QComboBox(self)
            combo.setProperty("inputIndex", i)

            combo.setFixedSize(150, 30)
            combo.addItems([
                "Select input",
                "cameraCapture",
                "desktopCapture",
                "stillImage",
                "colorGenerator",
                "noiseGenerator",
                "smpteBarsGenerator",
            ])
            # StackedWidget è un widget particolare che permette di visualizzare un solo widget alla volta
            # in pratica è una pila di widget
            # in questo caso viene utilizzato per visualizzare l'interfaccia grafica del'input selezionato
            # in base alla selezione della comboBox
            stacked_widget = QStackedWidget(self)
            placeholder_widget = QLabel("Select an option")
            stacked_widget.addWidget(placeholder_widget)
            stacked_widget.setCurrentIndex(0)
            checkbox = QCheckBox("Active")
            checkbox.setChecked(False)
            # ogni riga contiene un label, una comboBox, uno stackedWidget e un checkBox
            row = i - self.start
            self.layout.addWidget(label, row, 0)
            self.layout.addWidget(combo, row, 1)
            self.layout.addWidget(stacked_widget, row, 2)
            self.layout.addWidget(checkbox, row, 3)
            # i widget così creati vengono inseriti in alcune liste per poterli cercare facilmente
            self.combo_boxes.append(combo)
            self.stacked_widgets.append(stacked_widget)
            self.active_checkboxes.append(checkbox)

    @error_logger.log(log_level=logging.DEBUG)
    def initConnections(self):
        for checkbox, comboBox, stacked_widget in zip(self.active_checkboxes, self.combo_boxes, self.stacked_widgets):
            checkbox.toggled.connect(lambda state, c=comboBox, s=stacked_widget: self.toggleCapture(state, c, s))
            comboBox.currentIndexChanged.connect(self.inputComboBoxChanged)


    @error_logger.log(log_level=logging.DEBUG)
    def inputComboBoxChanged(self, index):
        """
        Ogni volta che l'utente cambia indice alla cmbBox, sta cambiando il tipo di Device,
        che può contenere a sua volta vari tipi di generatori, capture e player
        :param index:
        :return:
        """
        if index == 0:
            return
        sender = self.sender()  # il segnale che ha chiamato la funzione
        input_index = sender.property("inputIndex")  # recupera l'indice dell'input
        stack_index = input_index - self.start
        stacked_widget = self.stacked_widgets[stack_index]
        selected_input = sender.currentText()
        self.checkInput(input_index, selected_input, stacked_widget)

    @error_logger.log(log_level=logging.DEBUG)
    def checkInput(self, input_position, selected_input, stacked_widget):
        """
        Ogni device ha una sua interfaccia grafica. Se l'utente seleziona
        noise generator, piuttosto che video capture, l'interfaccia grafica
        cambia. Questa funzione si occupa attribuire la corretta interfaccia
        grafica al device selezionato.
        :param input_position:
        :param selected_input:
        :param stacked_widget:
        :return:
        """
        # Crea il nuovo InputDevice in base al tipo selezionato
        input_position = str(input_position)
        if selected_input == "colorGenerator":
            inputDevice = InputDevice_ColorGenerator(input_position, self)
        elif selected_input == "noiseGenerator":
            inputDevice = InputDevice_NoiseGenerator(input_position, self)
        elif selected_input == "stillImage":
            inputDevice = InputDevice_StillImagePlayer(input_position, self)
        elif selected_input == "smpteBarsGenerator":
            inputDevice = InputDevice_SmpteGenerator(input_position, self)
        elif selected_input == "desktopCapture":
            inputDevice = InputDevice_DesktopCapture(input_position, self)
        elif selected_input == "cameraCapture":
            inputDevice = InputDevice_CameraCapture(input_position, self)
        else:
            inputDevice = InputDevice_ColorGenerator(input_position, self)
        print(f"InputDevice: {inputDevice} added to position {input_position}")
        print(self.printVideoHubContent())
        # Aggiungi l'InputDevice al VideoHubData
        self.videoHubData.addInputDevice(input_position, inputDevice)
        # Aggiorna la visualizzazione dello stacked widget
        self.updateGridLayout(inputDevice, stacked_widget)

    @error_logger.log(log_level=logging.DEBUG)
    def updateGridLayout(self, inputDevice, stacked_widget):
        """
        Una volta confermato il tipo di inputDevice, viene aggiunto
        allo stacked widget l'interfaccia grafica del device selezionato
        :param inputDevice: la classe del device selezionato
        :param stacked_widget: lo stacked widget in cui inserire l'interfaccia grafica
        :return:
        """
        # Rimuovi i widget precedenti dallo stacked_widget (se presenti)
        for i in reversed(range(1, stacked_widget.count())):
            widget_to_remove = stacked_widget.widget(i)
            stacked_widget.removeWidget(widget_to_remove)
            widget_to_remove.deleteLater()
        # Aggiungi la graphicInterface dell'InputDevice allo stacked_widget
        stacked_widget.addWidget(inputDevice.graphicInterface)
        # Imposta l'indice corrente sul nuovo widget
        stacked_widget.setCurrentIndex(1)

    @error_logger.log(log_level=logging.INFO)
    def toggleCapture(self, state, comboBox, stacked_widget):
        logging.info(f"Toggle capture: {state}")
        logging.info(f"Sender: {comboBox}\nStackedWidget: {stacked_widget}\n{self.printVideoHubContent()}")
        input_index = comboBox.property("inputIndex")
        if state:  # Se l'utente attiva l'input
            logging.info(f"Activating input {input_index}")
            self.videoHubData.startInputDevice(input_index)
            comboBox.setEnabled(False)
        else:  # Se l'utente disattiva l'input
            logging.info(f"Deactivating input {input_index}")
            self.videoHubData.stopInputDevice(input_index)
            # Abilita la ComboBox
            comboBox.setEnabled(True)
        print(f"Input {input_index} toggled: {state}")
        print(self.printVideoHubContent())

    @error_logger.log(log_level=logging.INFO)
    def printVideoHubContent(self):
        returnString = "VideoHub content:\n"
        for index, _input in self.videoHubData.videoHubMatrix.items():
            returnString += f"Input {index}: {_input}\n"
        return returnString

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    videoHubData = VideoHubData018()
    videoHubData.tally_SIGNAL.connect(print)
    window = TabWidget_GenericInput(videoHubData, 5, 8)
    window.show()
    sys.exit(app.exec())
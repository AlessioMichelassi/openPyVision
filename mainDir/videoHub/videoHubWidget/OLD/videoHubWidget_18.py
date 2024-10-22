import logging
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from mainDir.inputDevice.captureDevice.inputDevice_cameraCapture import InputDevice_CameraCapture
from mainDir.inputDevice.generatorDevice.inputDevice_colorGenerator import InputDevice_ColorGenerator
from mainDir.inputDevice.generatorDevice.inputDevice_noiseGenerator import InputDevice_NoiseGenerator
from mainDir.inputDevice.generatorDevice.inputDevice_smpteGenerator import InputDevice_SmpteGenerator
from mainDir.inputDevice.captureDevice.inputDevice_desktopCapture import InputDevice_DesktopCapture
from mainDir.inputDevice.playerDevice.inputDevice_stillImagePlayerGenerator import \
    InputDevice_StillImagePlayer
from mainDir.videoHub.videoHubData018 import VideoHubData018
from mainDir.inputDevice.systemWidget.inputDevice_stingerPlayer import InputDevice_StingerAnimation


class VideoHubWidget018(QWidget):
    def __init__(self, _videoHubData, parent=None):
        super().__init__(parent)
        self.videoHubData = _videoHubData
        self.current_index = 0
        self.generator_list = [
            "Select input",
            "cameraCapture",
            "desktopCapture",
            "stillImage",
            "colorGenerator",
            "noiseGenerator",
            "smpteBarsGenerator",
        ]
        self.combo_boxes = []
        self.stacked_widgets = []
        self.active_checkboxes = []
        self.stingerLoaderList = []
        self.stinger_stacked_widgets = []
        self.mainLayout = QVBoxLayout(self)
        self.tabWidget = QTabWidget(self)
        self.initTabs()
        self.initUI()
        self.initConnections()

    def initTabs(self):
        """
        Inizializza i tab per i diversi tipi di input.
        :return:
        """
        # Tab 1: Inputs 1-4
        tab1 = QWidget()
        tab1.setLayout(self.returnGridLayout(start=1, end=4))
        self.tabWidget.addTab(tab1, "Inputs 1-4")

        # Tab 2: Inputs 5-8
        tab2 = QWidget()
        tab2.setLayout(self.returnGridLayout(start=5, end=8))
        self.tabWidget.addTab(tab2, "Inputs 5-8")

        # Tab 3: Caricamento Still Images (fino a 4)
        tab3 = QWidget()
        tab3.setLayout(self.returnStillLayout())
        self.tabWidget.addTab(tab3, "Still Images")

        # Tab 4: Caricamento Stingers (fino a 2)
        tab4 = QWidget()
        tab4.setLayout(self.returnStingerLayout())
        self.tabWidget.addTab(tab4, "Stingers")

    def initUI(self):
        self.mainLayout.addWidget(self.tabWidget)

    def initConnections(self):
        for checkbox, comboBox, stacked_widget in zip(self.active_checkboxes, self.combo_boxes, self.stacked_widgets):
            checkbox.toggled.connect(lambda state, c=comboBox, s=stacked_widget: self.toggleCapture(state, c, s))
            comboBox.currentIndexChanged.connect(self.inputComboBoxChanged)
        self.videoHubData.tally_SIGNAL.connect(self.getTally)

    def returnGridLayout(self, start=1, end=4):
        gridLayout = QGridLayout()
        for i in range(start, end + 1):
            label = QLabel(f"Input_{i}")
            label.setFont(QFont("Arial", 12, QFont.Weight.Bold))

            combo = QComboBox(self)
            combo.setFixedSize(150, 30)
            combo.addItems(self.generator_list)
            combo.currentIndexChanged.connect(self.inputComboBoxChanged)

            stacked_widget = QStackedWidget(self)
            placeholder_widget = QLabel("Select an option")
            stacked_widget.addWidget(placeholder_widget)

            btnInputAssign = QCheckBox("Active")

            gridLayout.addWidget(label, i - start, 0)
            gridLayout.addWidget(combo, i - start, 1)
            gridLayout.addWidget(stacked_widget, i - start, 2)
            gridLayout.addWidget(btnInputAssign, i - start, 3)

            self.combo_boxes.append(combo)
            self.stacked_widgets.append(stacked_widget)
            self.active_checkboxes.append(btnInputAssign)

        return gridLayout

    # STILL AND STINGER: TO DO CREATE DEVICE

    def returnStillLayout(self):
        # Layout per caricamento di 4 immagini fisse
        gridLayout = QGridLayout()  # Layout senza genitore
        for i in range(1, 5):  # 4 slot per le immagini fisse
            label = QLabel(f"Still Image {i}")
            label.setFont(QFont("Arial", 12, QFont.Weight.Bold))

            loadButton = QPushButton("Load Image")
            removeButton = QPushButton("Remove Image")

            gridLayout.addWidget(label, i - 1, 0)
            gridLayout.addWidget(loadButton, i - 1, 1)
            gridLayout.addWidget(removeButton, i - 1, 2)

        return gridLayout

    def returnStingerLayout(self):
        gridLayout = QGridLayout()
        for i in range(1, 3):
            label = QLabel(f"Stinger {i}")
            label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            inputDevice_Stinger = InputDevice_StingerAnimation(str(i), self)
            self.stingerLoaderList.append(inputDevice_Stinger)

            # Connetti il segnale con l'indice corretto
            inputDevice_Stinger.graphicInterface.stingerLoaded.connect(
                lambda _, idx=i: self.onStingerReady(idx)
            )

            # Creazione dello stacked_widget per lo stinger
            stacked_widget = QStackedWidget(self)
            stacked_widget.addWidget(inputDevice_Stinger.graphicInterface)
            stacked_widget.setCurrentIndex(0)

            # Aggiungi lo stacked_widget alla lista degli stingers
            self.stinger_stacked_widgets.append(stacked_widget)

            gridLayout.addWidget(label, i - 1, 0)
            gridLayout.addWidget(stacked_widget, i - 1, 1)
        return gridLayout

    def inputComboBoxChanged(self, index):
        if index == 0:
            return
        sender = self.sender()
        stack_index = self.combo_boxes.index(sender)
        stacked_widget = self.stacked_widgets[stack_index]
        selected_input = sender.currentText()

        input_position = stack_index + 1

        self.videoHubData.removeInputDevice(input_position)

        # Crea il nuovo InputDevice in base al tipo selezionato
        inputDevice = None
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

        if inputDevice:
            # Aggiungi l'InputDevice al VideoHubData
            self.videoHubData.addInputDevice(input_position, inputDevice)

            # Rimuovi i widget precedenti dallo stacked_widget (se presenti)
            for i in reversed(range(1, stacked_widget.count())):
                widget_to_remove = stacked_widget.widget(i)
                stacked_widget.removeWidget(widget_to_remove)
                widget_to_remove.deleteLater()
            # Aggiungi la graphicInterface dell'InputDevice allo stacked_widget
            stacked_widget.addWidget(inputDevice.graphicInterface)
            # Imposta l'indice corrente sul nuovo widget
            stacked_widget.setCurrentIndex(1)
        else:
            # Torna al widget segnaposto
            stacked_widget.setCurrentIndex(0)

    def toggleCapture(self, state, comboBox, stacked_widget):
        input_index = self.combo_boxes.index(comboBox) + 1
        if state:  # Se l'utente attiva l'input
            logging.info(f"Activating input {input_index}")
            self.videoHubData.startInputDevice(input_index)
            comboBox.setEnabled(False)
        else:  # Se l'utente disattiva l'input
            logging.info(f"Deactivating input {input_index}")
            self.videoHubData.stopInputDevice(input_index)
            # Abilita la ComboBox
            comboBox.setEnabled(True)
        self.printVideoHubContent()

    def onStingerReady(self):
        """
        Callback quando un nuovo stinger è pronto. Prende l'ultimo stingerLoaderWidget aggiunto alla lista
        e la posizione è l'indice dell'ultimo elemento della lista +1.
        :return:
        """
        inputDevice = self.stingerLoaderList[-1]
        inputPosition = len(self.stingerLoaderList)
        self.videoHubData.addStingerPlayer(inputPosition, inputDevice)
        # Usa la lista degli stinger_stacked_widgets
        stacked_widget = self.stinger_stacked_widgets[inputPosition - 1]
        # Aggiorna lo stacked_widget per mostrare l'interfaccia grafica dello stinger
        stacked_widget.setCurrentIndex(1)
        self.printVideoHubContent()

    def getTally(self, tally_data):
        logging.info(f"VIDEOHUBWIDGET -Received tally data: {tally_data}")
        sender = tally_data.get('sender')
        if sender != 'videoHub':
            cmd = tally_data.get('cmd')
            position = tally_data.get('position')
            if cmd == 'inputAdded':
                logging.info(f"Input added at position {position}")
            elif cmd == 'inputRemoved':
                logging.info(f"VIDEOHUBWIDGET -Input removed from position {position}")
            else:
                logging.warning(f"VIDEOHUBWIDGET -Invalid command from VideoHub: {cmd}\n{tally_data}")

    def printVideoHubContent(self):
        logging.info("VIDEOHUBWIDGET -Video Hub content:")
        for index, _input in self.videoHubData.videoHubMatrix.items():
            logging.info(f"Input {index}: {_input.getName()} - Type: {_input.getType()}")

    def blockSignals(self, block):
        """
        Metodo helper per disabilitare/abilitare i segnali dei widget.
        """
        for combo_box in self.combo_boxes:
            combo_box.blockSignals(block)
        for checkbox in self.active_checkboxes:
            checkbox.blockSignals(block)


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication

    app = QApplication([])
    videoHubData = VideoHubData018()
    widget = VideoHubWidget018(videoHubData)
    widget.show()
    app.exec()

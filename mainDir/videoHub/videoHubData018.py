import logging
import sys

from PyQt6.QtCore import QObject, pyqtSignal, QMetaObject, pyqtSlot, Qt, QTimer
from PyQt6.QtWidgets import QApplication

from mainDir.errorClass.loggerClass import ErrorClass, error_logger
from mainDir.inputDevice.generatorDevice.inputDevice_blackGenerator import InputDevice_BlackGenerator
from mainDir.inputDevice.generatorDevice.inputDevice_colorGenerator import InputDevice_ColorGenerator
from mainDir.inputDevice.generatorDevice.inputDevice_noiseGenerator import InputDevice_NoiseGenerator
from mainDir.inputDevice.generatorDevice.inputObject.generator_Black import BlackGenerator
from mainDir.inputDevice.playerDevice.inputDevice_stillImagePlayerGenerator import \
    InputDevice_StillImagePlayer
from mainDir.inputDevice.systemWidget.inputDevice_stingerPlayer import InputDevice_StingerPlayer_mb


class VideoHubData018(QObject):
    _blackSignal = None
    tally_SIGNAL = pyqtSignal(dict, name="tallySignal")

    @error_logger.log(log_level=logging.INFO)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.videoHubMatrix = {}
        error_logger.log("************* VIDEOHUBDATA *************")
        error_logger.log("VIDEOHUBDATA -Creating default black inputs")
        for i in range(0, 9):
            self.addInputDevice(i, self.createDefaultBlackInput(f"Black_{i}"))
        for i in range(0, 5):
            self.addStingerPlayer(i, self.createDefaultBlackInput(f"Black_Stinger_{i}"))
        for i in range(0, 5):
            self.addStillPlayer(i, self.createDefaultBlackInput(f"Black_StillImage_{i}"))
        error_logger.log("************* RND VIDEO HUB INIT *************")

    @staticmethod
    def createDefaultBlackInput(name):
        blackInput = BlackGenerator()
        inputDevice = InputDevice_BlackGenerator(f"{name}", blackInput)
        inputDevice.start()
        return inputDevice

    @error_logger.log(log_level=logging.INFO)
    def addInputDevice(self, position, inputDevice):
        """
        This adds an input device to the video hub matrix at the given position,
        but only if it is different from the current one.
        """
        position = str(position)
        current_device = self.getInputDevice(position)
        if current_device and current_device.getType() == inputDevice.getType():
            logging.info(f"Input device at position {position} already exists with the same type.")
            return
        logging.info(f"VIDEOHUBDATA - Adding new input device at position {position}")
        self.videoHubMatrix[position] = inputDevice

    @error_logger.log(log_level=logging.DEBUG)
    def getInputDevice(self, position):
        position = str(position)
        return self.videoHubMatrix.get(position)

    @error_logger.log(log_level=logging.DEBUG)
    def removeInputDevice(self, position):
        position = str(position)
        currentDevice = self.getInputDevice(position)
        if currentDevice:
            currentDevice.stop()
        self.videoHubMatrix[position] = self.createDefaultBlackInput(f"Black_{position}")

    @error_logger.log(log_level=logging.DEBUG)
    def startInputDevice(self, position):
        position = str(position)
        inputDevice = self.videoHubMatrix.get(position)
        print(f"inputDevice start: {inputDevice} - position: {position}")
        if inputDevice and inputDevice.getThread() and not inputDevice.getThread().isRunning():
            inputDevice.start()
            logging.info(f"VIDEOHUBDATA -Thread started for input at position {position}")
        self.emitTallySignal("inputChanged", position)

    @error_logger.log(log_level=logging.INFO)
    def stopAllDevices(self):
        """
        Ferma tutti i dispositivi attivi nel video hub matrix.
        """
        for position, device in self.videoHubMatrix.items():
            if device and device.getThread() and device.getThread().isRunning():
                device.stop()
                logging.info(f"VIDEOHUBDATA - Stopped input at position {position}")

    @error_logger.log(log_level=logging.INFO)
    def addStingerPlayer(self, position, inputDevice):
        stinger_position = f"stinger{position}"
        current_device = self.getInputDevice(stinger_position)

        # Verifica se l'oggetto esiste già con lo stesso tipo
        if current_device and current_device.getType() == inputDevice.getType():
            logging.info(f"Input device at position {stinger_position} already exists with the same type.")
            return

        # Aggiunta dell'oggetto Stinger al VideoHub Matrix
        logging.info(f"VIDEOHUBDATA - Adding new input device at position {stinger_position}")
        self.videoHubMatrix[stinger_position] = inputDevice

        # Verifica che l'oggetto sia un'istanza corretta di InputDevice_StingerAnimation
        if isinstance(inputDevice, InputDevice_StingerPlayer_mb):
            logging.info(f"Stinger added at position {stinger_position}.")
            self.emitTallySignal("stingerReady", position)
        else:
            logging.error(
                f"Failed to add stinger. Input device at position {stinger_position} is not a valid stinger object.")

    @error_logger.log(log_level=logging.DEBUG)
    def removeStingerPlayer(self, position):
        stinger_position = f"stinger{position}"
        currentDevice = self.getInputDevice(stinger_position)
        if currentDevice and currentDevice.getThread() and currentDevice.getThread().isRunning():
            currentDevice.stop()
            logging.info(f"VIDEOHUBDATA - Thread stopped for stinger at position {position}")

        self.videoHubMatrix[stinger_position] = self.createDefaultBlackInput(f"stinger{position}")
        self.emitTallySignal("stingerRemoved", stinger_position)
        logging.info(f"Stinger removed from position {stinger_position}.")

    @error_logger.log(log_level=logging.DEBUG)
    def startStingerPlayer(self, position):
        stinger_position = f"stinger{position}"
        current_device = self.getStingerPlayer(stinger_position)
        if current_device and current_device.getThread() and not current_device.getThread().isRunning():
            current_device.start()
            logging.info(f"VIDEOHUBDATA -Thread started for stinger at position {stinger_position}")
        self.emitTallySignal("stingerChanged", stinger_position)

    @error_logger.log(log_level=logging.DEBUG)
    def getStingerPlayer(self, position):
        # Verifica se la posizione è uno stinger
        stinger_position = f"stinger{position}"
        if stinger_position.startswith("stinger"):
            return self.videoHubMatrix.get(stinger_position)
        return self.videoHubMatrix.get(stinger_position)

    @error_logger.log(log_level=logging.DEBUG)
    def addStillPlayer(self, position, inputDevice):
        still_position = f"stillImage{position}"
        current_device = self.getInputDevice(still_position)
        if current_device and current_device.getType() == inputDevice.getType():
            logging.info(f"Input device at position {position} already exists with the same type.")
            return
        logging.info(f"VIDEOHUBDATA - Adding new input device at position {position}")
        self.videoHubMatrix[f"stillImage{position}"] = inputDevice
        self.emitTallySignal("stillImageReady", position)
        logging.info(f"Still image added at position {position}.")

    @error_logger.log(log_level=logging.DEBUG)
    def removeStillPlayer(self, position):
        still_position = f"stillImage{position}"
        currentDevice = self.getInputDevice(still_position)
        if currentDevice and currentDevice.getThread() and currentDevice.getThread().isRunning():
            currentDevice.stop()
            logging.info(f"VIDEOHUBDATA - Thread stopped for still image at position {position}")

        self.videoHubMatrix[still_position] = self.createDefaultBlackInput(f"Black_StillImage_{position}")
        self.emitTallySignal("stillImageRemoved", position)
        logging.info(f"Still image removed from position {position}.")

    @error_logger.log(log_level=logging.DEBUG)
    def startStillPlayer(self, position):
        position = str(position)
        inputDevice = self.getStillImage(position)
        if inputDevice and inputDevice.getThread() and not inputDevice.getThread().isRunning():
            inputDevice.start()
            logging.info(f"VIDEOHUBDATA -Thread started for still image at position {position}")
        self.emitTallySignal("stillImageChanged", position)

    @error_logger.log(log_level=logging.DEBUG)
    def getStillImage(self, position):
        if self.videoHubMatrix.get(f"stillImage{position}"):
            return self.videoHubMatrix.get(f"stillImage{position}")
        else:
            logging.error(f"Posizione still image non valida: {position}")
            return None

    def emitTallySignal(self, cmd, position):
        tally_status = {
            'sender': 'videoHub',
            'cmd': cmd,
            'position': position,
        }
        print(f"Emitting tally signal: {tally_status}")
        self.tally_SIGNAL.emit(tally_status)

    @error_logger.log(log_level=logging.INFO)
    def parseTallySignal(self, data):
        """
        This function parses the tally signal and performs the action accordingly.
        """
        cmd = data['cmd']
        position = data['position']

        if cmd == "startInput":
            logging.info(f"VIDEOHUBDATA -Starting input at position {position}")
            self.startInputDevice(position)
        elif cmd == "stopInput":
            logging.info(f"VIDEOHUBDATA -Stopping input at position {position}")
            self.stopInputDevice(position)

        elif cmd == "removeInput":
            logging.info(f"VIDEOHUBDATA -Removing input at position {position}")
            self.removeInputDevice(position)
        else:
            logging.warning(f"VIDEOHUBDATA -Unknown tally command: {cmd} for position {position}")

    @error_logger.log(log_level=logging.DEBUG)
    def serialize(self):
        data = {}
        for position, _input in self.videoHubMatrix.items():
            if _input:
                try:
                    data[position] = _input.serialize()
                except Exception as e:
                    logging.error(f"VIDEOHUBDATA -Error serializing input at position {position}: {e}")
        return data

    @error_logger.log(log_level=logging.DEBUG)
    def deserialize(self, data):
        for position, input_data in data.items():
            try:
                if input_data:  # Controlla che input_data non sia None
                    self.parseData(position, input_data)
            except Exception as e:
                logging.error(f"VIDEOHUBDATA -Error deserializing input at position {position}: {e}")

    @error_logger.log(log_level=logging.DEBUG)
    def parseData(self, position, input_data):
        """
        This function parses the input data and creates the corresponding input device.
        """
        input_type = input_data.get('type')  # Assumendo che ci sia una chiave 'type' nei dati
        if input_type == "BlackGenerator":
            input_device = self.default_black_input
            logging.debug(f"VIDEOHUBDATA -Black generator added at position {position}")
        elif input_type == "ColorGenerator":
            input_device = InputDevice_ColorGenerator("ColorGenerator")
            logging.debug(f"VIDEOHUBDATA -Color generator added at position {position}")
            input_device.deserialize(input_data)
        elif input_type == "NoiseGenerator":
            input_device = InputDevice_NoiseGenerator("NoiseGenerator")
            logging.debug(f"VIDEOHUBDATA -Noise generator added at position {position}")
            input_device.deserialize(input_data)
        elif input_type == "StillImagePlayer":
            input_device = InputDevice_StillImagePlayer("StillImagePlayer")
            logging.debug(f"VIDEOHUBDATA -Still image player added at position {position}")
            input_device.deserialize(input_data)
        else:
            logging.error(f"VIDEOHUBDATA -Unknown input type: {input_type} at position {position}")
            return

        # Aggiungi l'input device alla posizione corretta senza avviare il thread
        self.addInputDevice(position, input_device)

        # Emetti segnale di deserializzazione completata
        self.emitTallySignal("inputAdded", position)

        # Aggiungi l'input device alla posizione corretta senza avviare il thread
        self.addInputDevice(position, input_device)

        # Emetti segnale di deserializzazione completata
        self.emitTallySignal("inputAdded", position)


if __name__ == '__main__':
    app = QApplication([])

    videoHubData = VideoHubData018()
    videoHubData.tally_SIGNAL.connect(print)


    def run_test():
        print("start videoHubData")
        data = videoHubData.serialize()
        print(data)
        inputTest = InputDevice_NoiseGenerator("NoiseGenerator")
        videoHubData.addInputDevice(1, inputTest)
        print("add input device")
        videoHubData.startInputDevice(1)
        print("start input device")
        data = videoHubData.serialize()
        print(data)
        print("*** Test Stinger and Still Image ***")
        test = videoHubData.getInputDevice(1)
        print(f"input device: {test}")
        print("stop input device")
        data = videoHubData.serialize()
        print(data)
        print("removed input device")
        videoHubData.removeInputDevice(1)
        data = videoHubData.serialize()
        print(data)

        # Ferma tutti i dispositivi prima di uscire
        videoHubData.stopAllDevices()

        app.quit()  # Exit the application after the test


    # Schedule run_test to execute after the event loop starts
    QTimer.singleShot(0, run_test)
    sys.exit(app.exec())

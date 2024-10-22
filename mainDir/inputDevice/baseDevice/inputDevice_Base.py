import logging

import numpy as np
from PyQt6.QtCore import *
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import *

from mainDir.errorClass.loggerClass import ErrorClass

# Utilizziamo un'unica istanza di ErrorClass per i decoratori
error_logger = ErrorClass()


class InputSignalThread(QThread):
    """
    InputSignalThread gestisce un thread separato che esegue il ciclo di acquisizione dei frame dall'inputObject.
    Viene Orchestrato videoHubData.py.

    Args:
        input_id (int): L'ID dell'input.
        input_object (QObject): L'oggetto che genera o cattura i frame (es. NoiseGenerator, ColorGenerator, etc.).
    """

    @error_logger.log(log_level=logging.DEBUG)
    def __init__(self, input_name, input_object, parent=None):
        super().__init__(parent)
        self.input_id = input_name
        self.input_object = input_object  # Oggetto input che acquisisce i frame
        self.running = False


    def run(self):
        """
        Metodo principale del thread che cattura i frame dall'inputObject e dorme per ottenere ~60 FPS.
        """
        self.running = True
        while self.running:
            self.input_object.captureFrame()  # Acquisisce un nuovo frame
            self.msleep(10)  # Circa 60 FPS (1000ms / 60fps = 16.67ms)

    @error_logger.log(log_level=logging.DEBUG)
    def stop(self):
        """
        Ferma il thread in modo sicuro.
        """
        self.running = False
        self.quit()
        self.wait()


    def getFrame(self):
        """
        Restituisce il frame corrente dall'inputObject.
        """
        return self.input_object.getFrame()


class InputDevice_BaseClass(QObject):
    """
    InputDevice_BaseClass rappresenta un dispositivo di input generico nel mixer video.
    Si occupa di mettere insieme più classi che creano un input:
        - inputObject (NoiseGenerator, ColorGenerator, etc.)
        - thread (InputSignalThread)
        - interfaccia grafica (es. NoiseGeneratorWidget, ColorGeneratorWidget, etc.)

    In pratica inputDevice è l'interfaccia software per accedere correttamente all'inputObject,
    gestire il thread e quando l'utente interagisce con l'interfaccia grafica, lo fa passando
    informazioni all'inputDevice che aggiorna così l'inputObject.

    Per questo motivo esistono due segnali distinti nell'inputObject:
        - typeChanged
        - paramsChanged
    Alcuni generatori o capture devices possono in realtà avere più tipi di generatori o capture:

    NoiseGenerator:
                   - RandomNoiseGenerator
                   - SaltAndPepperNoiseGenerator
                   - grainNoiseGenerator

    l'interfaccia grafica semplifica la scelta del tipo di input, quando però selezioniamo un generatore di rumore
    casuale, piuttosto che un noise salt and pepper (fanno parte della stessa tipologia di generatori
    ma in realtà sono classi diverse), dobbiamo aggiornare l'inputObject con il nuovo tipo di generatore.
    Questo è il motivo per cui esiste il segnale typeChanged.

    La stessa cosa avviene con altre Device come colorGenerator (è possibile avere un colore solido, un gradiente,
    un pattern, ecc.) o con i desktop Capture dove quando ad esempio passiamo dalla cattura dello schermo alla cattura
    di un altro ho visto che è utile avere un segnale typeChanged che crea un nuovo oggetto di cattura, cancellando il
    precedente.

    Ovviamente ogni classe di generatori, capture e player ha i suoi parametri distintivi. E' possibile regolare
    alcune impostazioni tramite l'interfaccia grafica (grandezza della grana, velocità del rumore, colore del gradiente,
    ecc.). Ogni volta che viene cambiato un parametro tramite interfaccia grafica, viene emesso
    il segnale paramsChanged.

    Signals:
        tally_SIGNAL (dict): Segnale emesso per notificare lo stato o comandi del dispositivo.

    Attributes:
        input_position (int): La posizione dell'input nel sistema di input.
        _name (str): Nome dell'input (es. Input_1, Input_2, etc.).
        _nickname (str): Nickname dell'input (es. Cam1, etc.).
        _input_type_name (str): Tipo di input (es. NoiseGenerator, ColorGenerator).
        _input_object (QObject): L'oggetto che genera i frame.
        _thread (InputSignalThread): Thread per gestire l'acquisizione dei frame.
    """
    tally_SIGNAL = pyqtSignal(dict, name="tallySignal")
    blackImage = np.zeros((1080, 1920, 3), np.uint8)  # Immagine nera di default

    @error_logger.log(log_level=logging.DEBUG)
    def __init__(self, inputPosition, parent=None):
        """
        Inizializza un nuovo InputDevice_BaseClass.
        Args:
            inputPosition (int): La posizione del dispositivo di input.
        """
        super().__init__(parent)
        self.input_position = inputPosition
        self._name = f"InputDevice_{inputPosition}"
        self._nickname = f"Input_{inputPosition}"
        self._input_type_name = None
        self._input_object = None
        self._graphic_interface = None
        self._thread = None

    @error_logger.log(log_level=logging.DEBUG)
    def setName(self, name):
        """
        Imposta il nome dell'input device (es. Input_1).
        di default è settato su InputDevice_{inputPosition}.
        """
        if self.getThread() and self.getThread().isRunning():
            self.emitTallySignal("warning", "Thread is running; cannot change name.")
            logging.warning("Thread is running; cannot change name.")
            return
        self._name = name

    @error_logger.log(log_level=logging.DEBUG)
    def getName(self):
        """
        Restituisce il nome dell'input device (es. Input_1).
        """
        return self._name

    @error_logger.log(log_level=logging.DEBUG)
    def getType(self):
        """
        Restituisce il tipo dell'inputObject (es. NoiseGenerator) se è stato già impostato,
        altrimenti restituisce None.
        """
        return self._input_object.__class__.__name__ if self._input_object else None

    @error_logger.log(log_level=logging.DEBUG)
    def setNickname(self, nickname):
        """
        Ogni InputDevice ha un nome che di default include la Posizione dell'input.
        Si può impostare un nickName che è più descrittivo e che viene visualizzato
        nell'interfaccia di Mr Keyboard.
        Imposta un nickname per l'input device (es. Cam1).
        """
        self._nickname = nickname

    @error_logger.log(log_level=logging.DEBUG)
    def getNickname(self):
        """
        Restituisce il nickname dell'input device (es. Cam1).
        """
        return self._nickname

    @error_logger.log(log_level=logging.DEBUG)
    def setInputObject(self, inputObject):
        """
        Imposta l'oggetto di input (es. NoiseGenerator, ColorGenerator).

        Args:
            inputObject (QObject): L'oggetto che acquisisce o genera i frame.
        """
        self._input_object = inputObject
        self._input_type_name = inputObject.__class__.__name__
        # Se un thread esiste già e sta funzionando, fermalo prima di cambiare l'input
        if self._thread:
            self._thread.stop()  # Ferma il thread corrente se è in esecuzione
            self.emitTallySignal("warning", "Input object changed; thread stopped.")
            logging.warning("Input object changed; thread stopped.")
        self.setThread(inputObject)

    @error_logger.log(log_level=logging.DEBUG)
    def getInputObject(self):
        """
        Restituisce l'oggetto di input corrente.
        """
        return self._input_object

    @error_logger.log(log_level=logging.DEBUG)
    def setThread(self, inputObject):
        """
        Imposta il thread per gestire l'acquisizione dei frame dall'oggetto di input.

        Args:
            inputObject (QObject): L'oggetto di input (es. NoiseGenerator).
        """
        self._thread = InputSignalThread(self._name, inputObject)
        logging.info(f"Thread creato per {self._name} ({self._input_type_name}) alla posizione {self.input_position}.")

    @error_logger.log(log_level=logging.DEBUG)
    def getThread(self):
        """
        Restituisce il thread attualmente associato all'input device.
        """
        return self._thread

    @error_logger.log(log_level=logging.DEBUG)
    def setGraphicInterface(self, graphicInterface):
        """
        Imposta l'interfaccia grafica per l'input device.
        Ogni GraphicInterface può avere più tipi di input ad esempio:
        può avere un NoiseGenerator, un SaltAndPepperNoiseGenerator, un GrainNoiseGenerator, ecc.
        Ogni input ha la sua interfaccia grafica che permette di regolare i parametri del generatore.
        Di solito type Change arriva da videoHubWidget, mentre paramsChanged arriva dall'interfaccia grafica
        e definisce i parametri del generatore.
        Args:
            graphicInterface (QWidget): L'interfaccia grafica per l'input device.
        """
        self._graphic_interface = graphicInterface
        self._graphic_interface.TypeChanged.connect(self.OnChangeType)
        self._graphic_interface.ParamsChanged.connect(self.OnChangeParams)

    @error_logger.log(log_level=logging.DEBUG)
    def getGraphicInterface(self):
        """
        Restituisce l'interfaccia grafica dell'input device.
        """
        return self._graphic_interface

    @error_logger.log(log_level=logging.DEBUG)
    def OnChangeType(self, inputObject):
        """
        Quando viene cambiato il tipo di inputObject, viene
        chiamato questo metodo per fermare il thread corrente e
        e assegnare un nuovo inputObject.
        :param inputObject:
        :return:
        """
        if self.getInputObject:
            self.stop()
        self.setInputObject(inputObject)
        self.start()

    @error_logger.log(log_level=logging.DEBUG)
    def OnChangeParams(self, params):
        """
        Metodo chiamato quando i parametri dell'inputObject vengono cambiati dall'interfaccia grafica.

        Args:
            params (dict): Dizionario contenente i nuovi parametri.
        """
        if self._input_object:
            self._input_object.setParams(params)
        else:
            logging.warning("No input object set; cannot change parameters.")

    @error_logger.log(log_level=logging.DEBUG)
    def start(self):
        """
        Avvia il thread che cattura i frame dall'input object.
        Generalmente il viene avviato e fermato da videoHubData.py.
        """
        if self._thread and not self._thread.isRunning():
            self._thread.start()
            self.emitTallySignal("info", "Thread started.")
            logging.info(f"Thread avviato per {self._name} ({self._input_type_name})")

    @error_logger.log(log_level=logging.DEBUG)
    def stop(self):
        """
        Ferma il thread che cattura i frame.
        """
        if self._thread and self._thread.isRunning():
            self._thread.stop()
            logging.info(f"Thread fermato per {self._name} ({self._input_type_name})")


    @error_logger.log(log_level=logging.DEBUG)
    def captureFrame(self):
        """
        Cattura un frame dall'input object.
        """
        if self._input_object:
            if self.getThread() and self.getThread().isRunning():
                return self._input_object.captureFrame()
            else:
                self.emitTallySignal("warning", "Thread is not running; cannot capture frame.")
                logging.warning("Thread is not running; cannot capture frame.")
                return self.blackImage
        else:
            self.emitTallySignal("warning", "Input object not set; cannot get frame.")
            logging.warning("Input object not set; cannot get frame.")
            return self.blackImage

    @error_logger.log(log_level=logging.DEBUG)
    def getFrame(self):
        """
        Restituisce il frame corrente dall'input object.
        """
        if self._input_object:
            if self.getThread() and self.getThread().isRunning():
                return self._input_object.getFrame()
            else:
                self.emitTallySignal("warning", "Thread is not running; cannot get frame.")
                logging.warning("Thread is not running; cannot get frame.")
                return self.blackImage
        else:
            self.emitTallySignal("warning", "Input object not set; cannot get frame.")
            logging.warning("Input object not set; cannot get frame.")
            return self.blackImage

    @error_logger.log(log_level=logging.DEBUG)
    def getFps(self):
        """
        Restituisce il frame rate attuale dell'input object.
        """
        if self._input_object:
            return self._input_object.getFps()
        else:
            return 0

    @error_logger.log(log_level=logging.DEBUG)
    def emitTallySignal(self, cmd, message):
        """
        Emette un segnale tally con un comando e un messaggio.

        Args:
            cmd (str): Il comando da inviare (es. 'info', 'warning').
            message (str): Il messaggio associato al comando.
        """
        tally_status = {
            'sender': f"Input_{self.input_position}",
            'cmd': cmd,
            'message': message
        }
        try:
            self.tally_SIGNAL.emit(tally_status)
        except Exception as e:
            logging.error(f"Error emitting tally signal: {e}")

    @error_logger.log(log_level=logging.DEBUG)
    def serialize(self):
        """
        Serializza l'input device in un dizionario.

        Returns:
            dict: Dati serializzati dell'input device.
        """
        return {
            'name': self._name,
            'nickname': self._nickname,
            'type': self._input_type_name,
            'inputObject': self._input_object.serialize() if self._input_object else None
        }

    @error_logger.log(log_level=logging.DEBUG)
    def deserialize(self, data):
        """
        Deserializza l'input device da un dizionario.

        Args:
            data (dict): Dati serializzati.
        """
        self._name = data["name"]
        self._nickname = data["nickname"]
        self._input_type_name = data["type"]
        # Deserializza l'input object se esiste
        if "inputObject" in data and data["inputObject"]:
            self._input_object.deserialize(data["inputObject"])
        logging.info(f"Input device {self._name} deserialization.")

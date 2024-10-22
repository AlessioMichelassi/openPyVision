import json
import logging
import os
import cv2
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from mainDir.errorClass.loggerClass import ErrorClass, error_logger
from mainDir.inputDevice.systemWidget.inputObject.inputObject_StingerPlayer import \
    InputObject_StingerPlayerForMixBus
from mainDir.inputDevice.systemWidget.threadLoader.asyncCacheLoader import AsyncCacheLoader
from mainDir.inputDevice.systemWidget.threadLoader.cacheWorker import CacheWorker
from mainDir.inputDevice.systemWidget.threadLoader.progressDisplay import ProgressDisplay
from mainDir.inputDevice.systemWidget.threadLoader.stingerLoaderV04T import StingerLoaderV04T


class StingerLoaderWidget(QWidget):
    """
    StingerLoaderWidget è un widget per caricare, salvare e gestire animazioni stinger all'interno di un sistema Mix Bus.

    Signals:
        typeChanged (dict): Segnale emesso quando l'inputObject cambia tipo.
        paramsChanged (dict): Segnale emesso quando i parametri dell'inputObject cambiano.
        stingerLoaded (QObject): Segnale emesso quando lo stinger è stato caricato correttamente.
    """
    name = "StingerLoader"
    stingerLoaded = pyqtSignal(name="stingerLoaded")
    typeChanged = pyqtSignal(dict, name="typeChanged")
    paramsChanged = pyqtSignal(dict, name="paramsChanged")
    isCached = False

    @error_logger.log(log_level=logging.DEBUG)
    def __init__(self, _inputDevice, name="StingerLoader1", parent=None, stingerNumber=1):
        super().__init__(parent)
        """
        Inizializza il widget StingerLoaderWidget.

        Args:
            name (str): Nome del loader (default: "StingerLoader1").
            parent (Optional[QWidget]): Il widget padre (default: None).
        """
        super().__init__(parent)
        self.inputDevice = _inputDevice
        self.type = "StingerLoader"
        self.name = name
        self.cacheDirectory = None
        self.stingerNumber = stingerNumber
        self.loader = None
        self.cacheWorker = None
        self.progressDisplay = None
        self.cacheLoader = None

        self.configDialog = None
        # In questo caso l'utente può scegliere se salvare il cache o meno
        # del precalcolo dell'alfa inversa e pre-moltiplicazione. Se lo salva
        # in params vengono salvate le directory di salvataggio, se non lo fa
        # vengono passati a inputDevice solo i frame precalcolati.
        self.currentParams = {
            "stingerDirectory": "",
            "premultiplyDirectory": "",
            "invAlphaDirectory": "",
        }

        # Elementi UI
        self.btnLoadNewStinger = QPushButton("Load New Stinger", self)
        self.btnLoadCachedStinger = QPushButton("Load Cached Stinger", self)
        self.lneImagePath = QLineEdit("", self)
        self.btnCache = QPushButton("Save to Cache", self)
        self.btnCache.setEnabled(False)

        self.initUI()
        self.initConnections()

    @error_logger.log(log_level=logging.DEBUG)
    def initUI(self):
        """
        Inizializza l'interfaccia utente del widget.
        """
        layout = QHBoxLayout(self)
        layout.addWidget(self.lneImagePath)
        layout.addWidget(self.btnLoadNewStinger)
        layout.addWidget(self.btnLoadCachedStinger)
        layout.addWidget(self.btnCache)
        self.setLayout(layout)

    @error_logger.log(log_level=logging.DEBUG)
    def initConnections(self):
        """
        Inizializza le connessioni dei segnali tra i widget e le funzioni di gestione degli eventi.
        """
        self.btnLoadNewStinger.clicked.connect(self.onLoadDirectory)
        self.btnLoadCachedStinger.clicked.connect(self.onLoadCachedStinger)
        self.btnCache.clicked.connect(self.onBtnCache)

    @error_logger.log(log_level=logging.DEBUG)
    def onLoadDirectory(self, _=None):
        """
        Apre una finestra di dialogo per selezionare la directory dello stinger e inizia il caricamento delle immagini.
        """
        directory = QFileDialog.getExistingDirectory(self, "Select Stinger Directory")
        if directory:
            self.lneImagePath.setText(directory)
            self.startImageProcessing(directory)

    @error_logger.log(log_level=logging.DEBUG)
    def startImageProcessing(self, directory):
        """
        Avvia il caricamento e la gestione delle immagini nella directory dello stinger.

        Args:
            directory (str): Directory contenente le immagini dello stinger.
        """
        logging.info(f"Processing directory: {directory}")

        if not os.path.isdir(directory):
            logging.error(f"Error: Directory does not exist: {directory}")
            return

        if self.loader:
            self.loader.stop()
            self.loader.wait()

        self.loader = StingerLoaderV04T(directory)
        self.progressDisplay = ProgressDisplay(self.loader, title="Loading Stinger", message="Loading Stinger...")
        self.progressDisplay.show()

        self.loader.stingerReady.connect(self.onStingerReady)
        self.loader.start()

    @error_logger.log(log_level=logging.DEBUG)
    def onStingerReady(self):
        """
        Funzione di callback invocata quando il caricamento dello stinger è completato.
        """
        logging.info("Loading process completed.")
        inputObject = InputObject_StingerPlayerForMixBus(None, position=self.stingerNumber)
        self.inputDevice.setInputObject(inputObject)

        self.inputDevice.setStingerPremultipliedImages(self.loader.stingerPreMultipliedImages)
        self.inputDevice.setStingerInvAlphaImages(self.loader.stingerInvAlphaImages)
        self.btnCache.setEnabled(True)
        self.progressDisplay.close()
        self.stingerLoaded.emit()

    def closeProgressDisplay(self):
        """
        Chiude la finestra di dialogo di avanzamento.
        """
        if self.progressDisplay:
            self.progressDisplay.close()

    @error_logger.log(log_level=logging.DEBUG)
    def onBtnCache(self, _=None):
        """
        Apre la finestra di dialogo per selezionare la directory di cache e salva lo stinger nella cache.
        """
        directory = QFileDialog.getExistingDirectory(self, "Select Cache Directory")
        if directory:
            self.cacheDirectory = directory

            if self.cacheWorker:
                self.cacheWorker.stop()
                self.cacheWorker.wait()

            self.cacheWorker = CacheWorker(self.saveToCache)
            self.cacheWorker.operationCompleted.connect(self.closeProgressDisplay)
            self.progressDisplay = ProgressDisplay(self.cacheWorker, title="Saving Cache", message="Saving to Cache...")
            self.progressDisplay.show()
            self.cacheWorker.start()

    @error_logger.log(log_level=logging.DEBUG)
    def saveToCache(self, progress_callback=None):
        """
        Salva le immagini pre-moltiplicate e inverse dello stinger nella cache selezionata.

        Args:
            progress_callback (Optional): Funzione callback per aggiornare la barra di avanzamento.
        """

        name = os.path.basename(self.lneImagePath.text())
        premultiply_directory = os.path.join(self.cacheDirectory, f"{name}_premultiply")
        inv_alpha_directory = os.path.join(self.cacheDirectory, f"{name}_invAlpha")

        os.makedirs(premultiply_directory, exist_ok=True)
        os.makedirs(inv_alpha_directory, exist_ok=True)

        total_images = self.inputDevice.getLength()
        for i, img in enumerate(self.inputDevice.getStingerPremultipliedImages()):
            cv2.imwrite(os.path.join(premultiply_directory, f"frame_{i:03d}.png"), img)
            if progress_callback:
                progress_callback.emit(int((i + 1) / total_images * 50))

        for i, img in enumerate(self.inputDevice.getStingerInvAlphaImages()):
            cv2.imwrite(os.path.join(inv_alpha_directory, f"frame_{i:03d}.png"), img)
            if progress_callback:
                progress_callback.emit(50 + int((i + 1) / total_images * 50))

        cache_data = {
            'isCached': True,
            'stingerFolder': self.lneImagePath.text(),
            'premultiplyDirectory': premultiply_directory,
            'invAlphaDirectory': inv_alpha_directory
        }
        with open(os.path.join(self.cacheDirectory, f"{name}.cachedStinger.json"), 'w') as f:
            json.dump(cache_data, f, indent=4)

        logging.info("Cache saved successfully.")
        self.inputDevice.setCacheData(cache_data)

    @error_logger.log(log_level=logging.DEBUG)
    def onLoadCachedStinger(self, _=None):
        """
        Apre una finestra di dialogo per caricare uno stinger precedentemente salvato in cache.
        """
        cache_file_path, _ = QFileDialog.getOpenFileName(self, "Open Cached Stinger JSON", "", "JSON Files (*.json)")
        if cache_file_path:
            with open(cache_file_path, 'r') as f:
                cache_data = json.load(f)

            stinger_folder = cache_data.get('stingerFolder')
            premultiply_directory = cache_data.get('premultiplyDirectory')
            inv_alpha_directory = cache_data.get('invAlphaDirectory')
            self.lneImagePath.setText(stinger_folder)
            logging.info(f"Stinger Folder: {stinger_folder}")
            logging.info(f"Premultiply Directory: {premultiply_directory}")
            logging.info(f"Inv Alpha Directory: {inv_alpha_directory}")

            if not os.path.isdir(stinger_folder):
                logging.error(f"Error: Stinger folder does not exist: {stinger_folder}")
                return

            self.startLoadingCachedImages(premultiply_directory, inv_alpha_directory)

    @error_logger.log(log_level=logging.DEBUG)
    def startLoadingCachedImages(self, premultiply_directory, inv_alpha_directory):
        """
        Avvia il caricamento delle immagini da cache.

        Args:
            premultiply_directory (str): Directory contenente le immagini pre-moltiplicate.
            inv_alpha_directory (str): Directory contenente le immagini alpha inverse.
        """
        if self.cacheLoader:
            self.cacheLoader.stop()
            self.cacheLoader.wait()

        self.cacheLoader = AsyncCacheLoader(premultiply_directory, inv_alpha_directory)
        self.progressDisplay = ProgressDisplay(self.cacheLoader, title="Loading Cached Images",
                                               message="Loading Cache...")
        self.progressDisplay.show()

        self.cacheLoader.imagesLoaded.connect(self.onCachedImagesLoaded)
        self.cacheLoader.operationCompleted.connect(self.progressDisplay.onOperationCompleted)
        self.cacheLoader.start()

    @error_logger.log(log_level=logging.DEBUG)
    def onCachedImagesLoaded(self, premultiplied_images, inv_alpha_images):
        """
        Callback invocato quando le immagini cached sono state caricate.

        Args:
            premultiplied_images (list): Lista delle immagini pre-moltiplicate caricate.
            inv_alpha_images (list): Lista delle immagini alpha inverse caricate.
        """
        self.inputDevice.setInputObject(InputObject_StingerPlayerForMixBus(None, self.stingerNumber))
        self.inputDevice.setStingerPremultipliedImages(premultiplied_images)
        self.inputDevice.setStingerInvAlphaImages(inv_alpha_images)

        self.btnCache.setEnabled(True)
        self.stingerLoaded.emit()

    @ErrorClass().log(log_level=logging.DEBUG)
    def closeEvent(self, event, _QCloseEvent=None):
        """
        Gestisce l'evento di chiusura del widget, fermando i caricamenti in corso.

        Args:
            event (QCloseEvent): Evento di chiusura.
        """
        if self.loader:
            self.loader.stop()
            self.loader.wait()

        if self.cacheWorker:
            self.cacheWorker.stop()
            self.cacheWorker.wait()

        super().closeEvent(event)

    @ErrorClass().log(log_level=logging.DEBUG)
    def serialize(self):
        """
        Serializza il widget e il suo inputObject.

        Returns:
            dict: Dati serializzati del widget.
        """
        return {
            'type': "StingerAnimationForMixBus",
            'params': {
                'isCached': self.isCached,
                'imagePath': self.lneImagePath.text(),
                'cachedPath': self.cacheDirectory,
                'inputObject': self.inputObject.serialize() if self.inputObject else None
            }
        }

    @ErrorClass().log(log_level=logging.DEBUG)
    def deserialize(self, data):
        """
        Deserializza i dati nel widget e nell'inputObject.

        Args:
            data (dict): Dati serializzati da deserializzare.
        """
        self.setName(data['name'])
        self.lneImagePath.setText(data['imagePath'])
        if data['inputObject']:
            self.inputObject = InputObject_StingerPlayerForMixBus(data['imagePath'], self.stingerNumber)
            self.inputObject.deserialize(data['inputObject'])


if __name__ == "__main__":
    from mainDir.inputDevice.systemWidget.inputDevice_stingerPlayer import InputDevice_StingerPlayer_mb
    app = QApplication([])
    inputDevice = InputDevice_StingerPlayer_mb("StingerLoader1")
    window = StingerLoaderWidget(inputDevice)
    window.typeChanged.connect(print)
    window.show()
    app.exec()

import logging

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from mainDir.outputs.openGLViewer015 import error_logger


class BaseConfigurationWidget(QWidget):
    # Segnale personalizzato per trasmettere variazioni di configurazione in tempo reale
    paramsChanged = pyqtSignal(dict)

    @error_logger.log(log_level=logging.DEBUG)
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.params = {}
        self.default_params = {}
        # inserendo i widget in questo layout,
        # si possono aggiungere i widget in ordine
        self.widget_layout = QVBoxLayout()
        self.applyButton = QPushButton("Apply", self)
        self.cancelButton = QPushButton("Cancel", self)
        self._initUI()
        self._initConnections()

        # Imposta la finestra sempre in primo piano
        self.setWindowFlags(self.windowFlags() | self.windowFlags().WindowStaysOnTopHint)

    @error_logger.log(log_level=logging.DEBUG)
    def _initUI(self):
        """Inizializza l'interfaccia utente comune."""
        # Layout per i pulsanti Apply e Cancel
        main_Layout = QVBoxLayout()
        main_Layout.addLayout(self.widget_layout)
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.applyButton)
        buttonLayout.addWidget(self.cancelButton)

        main_Layout.addLayout(buttonLayout)
        self.setLayout(main_Layout)

    @error_logger.log(log_level=logging.DEBUG)
    def _initConnections(self):
        self.applyButton.clicked.connect(self.applySettings)
        self.cancelButton.clicked.connect(self.close)

    @error_logger.log(log_level=logging.DEBUG)
    def setParams(self, params):
        """Metodo per impostare la configurazione iniziale."""
        self.params = params

    @error_logger.log(log_level=logging.DEBUG)
    def getParams(self):
        """Metodo per ottenere la configurazione attuale."""
        return self.params

    @error_logger.log(log_level=logging.DEBUG)
    def applySettings(self):
        """Applica le impostazioni attuali e trasmette il segnale di configurazione."""
        # Emetti il segnale di configurazione aggiornata
        self.paramsChanged.emit(self.params)


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    widget = BaseConfigurationWidget("Test Configuration Widget")
    widget.show()
    sys.exit(app.exec())
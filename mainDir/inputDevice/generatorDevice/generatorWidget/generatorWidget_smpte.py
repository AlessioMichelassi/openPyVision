import logging

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import *

from mainDir.inputDevice.baseDevice.baseClass.baseInputWidget import BaseInputWidget
from mainDir.outputs.openGLViewer015 import error_logger


class GeneratorWidget_Smpte(BaseInputWidget):
    """
        An InputDevice for managing the SMPTE generator.
        It brings together the thread, the input object, and the graphical interface,
        acting as the interface for the mixer.
        """
    name = "Smpte"
    inputDevice = None
    typeChanged = pyqtSignal(dict, name="typeChanged")
    paramsChanged = pyqtSignal(dict, name="paramsChanged")
    typeList = ["bars"]

    @error_logger.log(log_level=logging.DEBUG)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.configDialog = None
        self.currentConfig = {
            "type": "bars",
            "params": {}
        }
        self.btnConfig.setEnabled(False)


    @error_logger.log(log_level=logging.DEBUG)
    def onComboChanges(self, index):
        smpteType = self.cmbInputType.currentText()
        print(f"Smpte type changed to {smpteType}")
        self.paramsChanged.emit({'smpteType': smpteType})

    @error_logger.log(log_level=logging.DEBUG)
    def serialize(self):
        super().serialize()

    @error_logger.log(log_level=logging.DEBUG)
    def deserialize(self, data):
        super().deserialize(data)

if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    widget = GeneratorWidget_Smpte()
    widget.typeChanged.connect(print)
    widget.paramsChanged.connect(print)
    widget.show()
    sys.exit(app.exec())
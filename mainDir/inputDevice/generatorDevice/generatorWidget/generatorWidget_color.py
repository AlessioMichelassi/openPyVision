import logging

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from mainDir.inputDevice.baseDevice.baseClass.baseInputWidget import BaseInputWidget
from mainDir.outputs.openGLViewer015 import error_logger


class GeneratorWidget_Color(BaseInputWidget):
    name = "color"
    inputDevice = None
    typeChanged = pyqtSignal(dict, name="typeChanged")
    paramsChanged = pyqtSignal(dict, name="paramsChanged")
    typeList = ["random", "rgb", "black"]

    @error_logger.log(log_level=logging.DEBUG)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.configDialog = None
        self.currentParams = {
            "type": "random",
            "red": 0,
            "green": 0,
            "blue": 0
        }
        self.btnConfig.setEnabled(False)

    @error_logger.log(log_level=logging.DEBUG)
    def onComboChanges(self, index):
        currentType = self.cmbInputType.currentText()
        print(f"{self.name} type changed to {currentType}")
        if currentType == "rgb":
            self.currentParams.update({"type": "rgb"})
            self.btnConfig.setEnabled(True)
        elif currentType == "random":
            self.currentParams.update({"type": "random"})
            self.btnConfig.setEnabled(False)
        elif currentType == "black":
            self.currentParams.update({"type": "black"})
            self.btnConfig.setEnabled(False)
        self.typeChanged.emit({'currentType': currentType})

    @error_logger.log(log_level=logging.DEBUG)
    def onConfigClicked(self):
        color = QColorDialog.getColor()  # Mostra il selettore di colore
        if color.isValid():
            # Aggiorna anche il dizionario config
            self.currentParams.update({
                "red": color.red(),
                "green": color.green(),
                "blue": color.blue()
            })
            self.paramsChanged.emit(self.currentParams)

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
    widget = GeneratorWidget_Color()
    widget.typeChanged.connect(print)
    widget.paramsChanged.connect(print)
    widget.show()
    sys.exit(app.exec())

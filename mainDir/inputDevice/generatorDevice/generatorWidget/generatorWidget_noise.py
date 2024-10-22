import logging

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from mainDir.inputDevice.baseDevice.baseClass.baseInputWidget import BaseInputWidget
from mainDir.inputDevice.generatorDevice.generatorWidget.generatorDialog.configDialog_noise_Grain import \
    ConfigDialog_GrainNoise
from mainDir.inputDevice.generatorDevice.generatorWidget.generatorDialog.configDialog_noise_SaltAndPepper import \
    ConfigDialog_SaltAndPepperNoise


from mainDir.outputs.openGLViewer015 import error_logger




class GeneratorWidget_Noise(BaseInputWidget):
    name = "Noise"
    inputDevice = None
    typeChanged = pyqtSignal(dict, name="typeChanged")
    paramsChanged = pyqtSignal(dict, name="paramsChanged")
    typeList = ["Random", "Salt and Pepper", "Grain", "Gaussian"]

    @error_logger.log(log_level=logging.DEBUG)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.configDialog = None
        self.currentConfig = {
            "type": "Random",
            "params": {}
        }
        self.btnConfig.setEnabled(False)


    @error_logger.log(log_level=logging.DEBUG)
    def onComboChanges(self, index):
        super().onComboChanges(index)
        if self.cmbInputType.currentText() == "Random":
            self.btnConfig.setEnabled(False)
        else:
            self.btnConfig.setEnabled(True)

    @error_logger.log(log_level=logging.DEBUG)
    def onConfigClicked(self, *args, **kwargs):
        currentType = self.cmbInputType.currentText()
        if currentType == "Salt and Pepper":
            self.configDialog = ConfigDialog_SaltAndPepperNoise("Salt and Pepper")
            self.openDialog()
        elif currentType == "Grain":
            self.configDialog = ConfigDialog_GrainNoise("Grain Noise")
            self.openDialog()
        elif currentType == "Gaussian":
            pass
        else:
            return

    def openDialog(self):
        params = self.currentConfig.get("params", {})
        if params != {}:
            self.configDialog.setParams(params)
        self.configDialog.paramsChanged.connect(self.onParamsChanged)
        self.configDialog.show()

    def onParamsChanged(self, params):
        self.currentConfig["params"] = params
        self.paramsChanged.emit(self.currentConfig)



    @error_logger.log(log_level=logging.DEBUG)
    def serialize(self):
        currentType = self.cmbInputType.currentText()
        data = {
            'currentType': currentType,
        }
        if currentType in self.currentConfig:
            data['params'] = self.currentConfig[currentType]
        return data

    @error_logger.log(log_level=logging.DEBUG)
    def deserialize(self, data):
        currentType = data.get('currentType', 'Random')
        index = self.typeList.index(currentType) if currentType in self.typeList else 0
        self.cmbInputType.setCurrentIndex(index)
        params = data.get('params', {})
        self.currentConfig[currentType] = params



if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    widget = GeneratorWidget_Noise()

    widget.show()
    sys.exit(app.exec())

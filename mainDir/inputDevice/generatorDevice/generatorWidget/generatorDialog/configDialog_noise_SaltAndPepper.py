import logging

from mainDir.inputDevice.baseDevice.baseClass.baseConfigurationDialog import BaseConfigurationWidget
from mainDir.widgets.commonWidgets.commonWidget_DoubleSpinBox import CommonWidget_DoubleSpinBox
from mainDir.outputs.openGLViewer015 import error_logger


class ConfigDialog_SaltAndPepperNoise(BaseConfigurationWidget):

    @error_logger.log(log_level=logging.DEBUG)
    def __init__(self,title, parent=None):
        super().__init__(f"{title} Configuration", parent)
        self.params = {
            'salt_probability': 0.1,
            'pepper_probability': 0.1
        }
        self.saltSpinBox = CommonWidget_DoubleSpinBox("Salt Probability", self)
        self.pepperSpinBox = CommonWidget_DoubleSpinBox("Pepper Probability", self)
        self.default_params = self.params
        self.initUI()
        self.initConnections()

    @error_logger.log(log_level=logging.DEBUG)
    def initUI(self):
        self.saltSpinBox.initDefault(0.1, 0.0, 5.0)
        self.pepperSpinBox.initDefault(0.1, 0.0, 5.0)
        self.widget_layout.addWidget(self.saltSpinBox)
        self.widget_layout.addWidget(self.pepperSpinBox)

    @error_logger.log(log_level=logging.DEBUG)
    def initConnections(self):
        self.saltSpinBox.paramsChanged.connect(self.onParamsChanged)
        self.pepperSpinBox.paramsChanged.connect(self.onParamsChanged)

    @error_logger.log(log_level=logging.DEBUG)
    def setParams(self, params):
        super().setParams(params)
        self.saltSpinBox.setParams(self.params.get('salt_probability', 0.1), )
        self.pepperSpinBox.setParams(self.params.get('pepper_probability', 0.1))

    @error_logger.log(log_level=logging.DEBUG)
    def applySettings(self, *args, **kwargs):
        # I valori sono già aggiornati in self.config tramite le connessioni dei spin box
        if args or kwargs:
            print(f"Salt and Pepper Noise Configuration: {args}, {kwargs}")
        super().applySettings()

    @error_logger.log(log_level=logging.DEBUG)
    def onParamsChanged(self, params):
        self.params.update(params)
        self.paramsChanged.emit(self.params)


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication

    test = QApplication(sys.argv)
    dialog = ConfigDialog_SaltAndPepperNoise()
    dialog.paramsChanged.connect(print)
    dialog.show()
    sys.exit(test.exec())
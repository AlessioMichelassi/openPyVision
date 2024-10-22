import logging

from mainDir.inputDevice.baseDevice.baseClass.baseConfigurationDialog import BaseConfigurationWidget
from mainDir.widgets.commonWidgets.commonWidget_DoubleSpinBox import CommonWidget_DoubleSpinBox
from mainDir.outputs.openGLViewer015 import error_logger


class ConfigDialog_GrainNoise(BaseConfigurationWidget):
    grainSizeSpinBox: CommonWidget_DoubleSpinBox
    rSpeedSpinBox: CommonWidget_DoubleSpinBox
    gSpeedSpinBox: CommonWidget_DoubleSpinBox
    bSpeedSpinBox: CommonWidget_DoubleSpinBox
    rOffsetSpinBox: CommonWidget_DoubleSpinBox
    gOffsetSpinBox: CommonWidget_DoubleSpinBox
    bOffsetSpinBox: CommonWidget_DoubleSpinBox

    @error_logger.log(log_level=logging.DEBUG)
    def __init__(self, title, parent=None):
        super().__init__(f"{title} Configuration", parent)
        self.params = {
            'grain_size': 3,
            'r_speed': 2,
            'g_speed': 1,
            'b_speed': 3,
            'r_offset': 2,
            'g_offset': 0,
            'b_offset': 4
        }
        self.grainSize = CommonWidget_DoubleSpinBox("Grain Size", self)
        self.redSpeed = CommonWidget_DoubleSpinBox("Red Speed", self)
        self.greenSpeed = CommonWidget_DoubleSpinBox("Green Speed", self)
        self.blueSpeed = CommonWidget_DoubleSpinBox("Blue Speed", self)
        self.redOffset = CommonWidget_DoubleSpinBox("Red Offset", self)
        self.greenOffset = CommonWidget_DoubleSpinBox("Green Offset", self)
        self.blueOffset = CommonWidget_DoubleSpinBox("Blue Offset", self)

        self.default_params = self.params
        self.initUI()
        self.initConnections()

    @error_logger.log(log_level=logging.DEBUG)
    def initUI(self):
        self.grainSize.initDefault(3, 1, 10)
        self.redSpeed.initDefault(2, 0, 10)
        self.greenSpeed.initDefault(1, 0, 10)
        self.blueSpeed.initDefault(3, 0, 10)
        self.redOffset.initDefault(2, 0, 100)
        self.greenOffset.initDefault(0, 0, 100)
        self.blueOffset.initDefault(4, 0, 100)
        self.widget_layout.addWidget(self.grainSize)
        self.widget_layout.addWidget(self.redSpeed)
        self.widget_layout.addWidget(self.greenSpeed)
        self.widget_layout.addWidget(self.blueSpeed)
        self.widget_layout.addWidget(self.redOffset)
        self.widget_layout.addWidget(self.greenOffset)
        self.widget_layout.addWidget(self.blueOffset)


    @error_logger.log(log_level=logging.DEBUG)
    def initConnections(self):
        self.grainSize.paramsChanged.connect(self.onParamsChanged)
        self.redSpeed.paramsChanged.connect(self.onParamsChanged)
        self.greenSpeed.paramsChanged.connect(self.onParamsChanged)
        self.blueSpeed.paramsChanged.connect(self.onParamsChanged)
        self.redOffset.paramsChanged.connect(self.onParamsChanged)
        self.greenOffset.paramsChanged.connect(self.onParamsChanged)
        self.blueOffset.paramsChanged.connect(self.onParamsChanged)

    @error_logger.log(log_level=logging.DEBUG)
    def setParams(self, params):
        super().setParams(params)
        self.grainSize.setParams(self.params.get('grain_size', 3))
        self.redSpeed.setParams(self.params.get('r_speed', 2))
        self.greenSpeed.setParams(self.params.get('g_speed', 1))
        self.blueSpeed.setParams(self.params.get('b_speed', 3))
        self.redOffset.setParams(self.params.get('r_offset', 2))
        self.greenOffset.setParams(self.params.get('g_offset', 0))
        self.blueOffset.setParams(self.params.get('b_offset', 4))


    @error_logger.log(log_level=logging.DEBUG)
    def applySettings(self, *args, **kwargs):
        # I valori sono già aggiornati in self.config tramite le connessioni dei spin box
        if args or kwargs:
            print(f"grain Noise Configuration: {args}, {kwargs}")
        super().applySettings()

    @error_logger.log(log_level=logging.DEBUG)
    def onParamsChanged(self, params):
        self.params.update(params)
        self.paramsChanged.emit(self.params)


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication

    test = QApplication(sys.argv)
    dialog = ConfigDialog_GrainNoise()
    dialog.paramsChanged.connect(print)
    dialog.show()
    sys.exit(test.exec())



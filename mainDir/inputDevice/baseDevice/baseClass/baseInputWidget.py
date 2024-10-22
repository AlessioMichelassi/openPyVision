import logging

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from mainDir.errorClass.loggerClass import error_logger


class BaseInputWidget(QWidget):
    name = "default"
    inputDevice = None
    typeChanged = pyqtSignal(dict)
    paramsChanged = pyqtSignal(dict)
    typeList = []

    @error_logger.log(log_level=logging.DEBUG)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cmbInputType = QComboBox(self)
        self.btnConfig = QPushButton("Config", self)
        self.configDialog = None
        self.currentParams = {}
        self.initUI()
        self.initConnections()

    @error_logger.log(log_level=logging.DEBUG)
    def initUI(self):
        self.cmbInputType.addItems(self.typeList)
        main_layout = QHBoxLayout(self)
        label = QLabel(f"{self.name} Type", self)
        main_layout.addWidget(label)
        main_layout.addWidget(self.cmbInputType)
        main_layout.addWidget(self.btnConfig)
        self.setLayout(main_layout)

    @error_logger.log(log_level=logging.DEBUG)
    def initConnections(self):
        self.cmbInputType.currentIndexChanged.connect(self.onComboChanges)
        self.btnConfig.clicked.connect(self.onConfigClicked)

    @error_logger.log(log_level=logging.DEBUG)
    def onComboChanges(self, index):
        currentType = self.cmbInputType.currentText()
        print(f"{self.name} type changed to {currentType}")
        self.typeChanged.emit({'type': currentType})

    @error_logger.log(log_level=logging.DEBUG)
    def onConfigClicked(self):
        pass

    @error_logger.log(log_level=logging.DEBUG)
    def serialize(self):
        currentType = self.cmbInputType.currentText()
        data = {
            'currentType': currentType,
        }
        if currentType in self.currentParams:
            data['params'] = self.currentParams[currentType]
        return data

    @error_logger.log(log_level=logging.DEBUG)
    def deserialize(self, data):
        currentType = data.get('currentType', 'Random')
        index = self.typeList.index(currentType) if currentType in self.typeList else 0
        self.cmbInputType.setCurrentIndex(index)
        self.currentParams[currentType] = data.get('params', {})


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    widget = BaseInputWidget()

    widget.show()
    sys.exit(app.exec())

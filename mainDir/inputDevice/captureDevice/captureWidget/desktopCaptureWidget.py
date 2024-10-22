import logging

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from mainDir.inputDevice.baseDevice.baseClass.baseInputWidget import BaseInputWidget


class DesktopCaptureWidget(BaseInputWidget):
    name = "DesktopCapture"
    inputDevice = None
    typeChanged = pyqtSignal(dict, name="typeChanged")
    paramsChanged = pyqtSignal(dict, name="paramsChanged")
    typeList = []

    def __init__(self, parent=None):
        super().__init__(parent)
        self.screenRegion = (0, 0, 1920, 1080)
        self.configDialog = None
        self.screenList = self.getAvailableScreens()
        self.cmbInputType.addItems(self.screenList)
        self.btnConfig.setEnabled(False)
        self.currentConfig = {}


    def refreshScreenList(self):
        screenText = self.cmbInputType.currentText()
        self.screenList = self.getAvailableScreens()
        self.cmbInputType.addItems(self.screenList)
        try:
            self.cmbInputType.clear()
            index = self.screenList.index(screenText)
            self.cmbInputType.setCurrentIndex(index)
        except ValueError:
            logging.warning(f"Screen {screenText} is not available anymore")

    def onComboChanges(self, index):
        selected_device = self.cmbInputType.currentText()
        selectedIndex = self.cmbInputType.currentIndex()
        dictionary = {'type': selected_device, 'index': selectedIndex}
        self.typeChanged.emit(dictionary)
        print(f"CaptureWidget_Camera - onComboChanges: {selected_device} - {selectedIndex}")

    def onConfigClicked(self, *args, **kwargs):
        self.paramsChanged.emit({'type': self.cmbInputType.currentIndex()})



    @staticmethod
    def getAvailableScreens():
        screens = QGuiApplication.screens()
        screen_names = [screen.name() for screen in screens]
        return screen_names

    def updateInputObject(self):
        # Emette un segnale di cambio parametri
        self.paramsChanged.emit({
            'screenRegion': self.screenRegion
        })

    def serialize(self):
        super().serialize()

    def deserialize(self, data):
        super().deserialize(data)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    screenCaptureWidget = DesktopCaptureWidget()
    screenCaptureWidget.paramsChanged.connect(print)
    screenCaptureWidget.typeChanged.connect(print)
    screenCaptureWidget.show()
    sys.exit(app.exec())

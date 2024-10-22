
from PyQt6.QtCore import *

from mainDir.inputDevice.baseDevice.baseClass.baseInputWidget import BaseInputWidget
from mainDir.inputDevice.captureDevice.inputObject.deviceFinder.deviceUpdater import DeviceUpdater


class CaptureWidget_Camera(BaseInputWidget):
    name = "Capture"
    inputDevice = None
    typeChanged = pyqtSignal(dict, name="typeChanged")
    paramsChanged = pyqtSignal(dict, name="paramsChanged")
    typeList = []
    devices = {}

    def __init__(self, parent=None):
        super().__init__(parent)
        self.configDialog = None
        self.cameraDevice = parent
        self.deviceUpdater = DeviceUpdater(self)
        self.cmbInputType.setMinimumWidth(170)
        self.refreshDevice()
        self.btnConfig.setEnabled(True)

    def refreshDevice(self):
        self.deviceUpdater.start()
        self.deviceUpdater.finished.connect(self.populateCombo)

    def populateCombo(self, devices):
        self.devices = devices  # Store the devices dictionary
        self.typeList = [device['name'] for device in devices.values()]
        self.typeList.insert(0, "Select a device")
        self.cmbInputType.clear()
        self.cmbInputType.addItems(self.typeList)

    def onComboChanges(self, index):
        """
        Emette l'indice del device selezionato
        :param index:
        :return:
        """
        selected_device = self.cmbInputType.currentText()
        selectedIndex = self.cmbInputType.currentIndex()
        dictionary = {'type': selected_device, 'index': selectedIndex}
        self.typeChanged.emit(dictionary)
        print(f"CaptureWidget_Camera - onComboChanges: {selected_device}")

    def onConfigClicked(self, *args, **kwargs):
        self.paramsChanged.emit({'type': self.cmbInputType.currentIndex()})


    def serialize(self):
        super().serialize()

    
    def deserialize(self, data):
        super().deserialize(data)


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    widget = CaptureWidget_Camera()
    widget.typeChanged.connect(print)
    widget.paramsChanged.connect(print)
    widget.show()
    sys.exit(app.exec())

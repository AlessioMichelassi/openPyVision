from PyQt6.QtWidgets import QApplication

from mainDir.inputDevice.generatorDevice.inputDevice_smpteGenerator import InputDevice_SmpteGenerator
from mainDir.inputDevice.testInputDevice.baseTestDevice_InputDevice import InputDeviceAppTester

if __name__ == "__main__":
    app = QApplication([])
    tester = InputDeviceAppTester(InputDevice_SmpteGenerator("Smpte Generator"))
    tester.show()
    app.exec()
from PyQt6.QtWidgets import QApplication

from mainDir.inputDevice.testInputDevice.baseTestDevice_InputDevice import InputDeviceAppTester
from mainDir.inputDevice.generatorDevice.inputDevice_colorGenerator import InputDevice_ColorGenerator

if __name__ == "__main__":
    app = QApplication([])
    tester = InputDeviceAppTester(InputDevice_ColorGenerator("Color Generator"))
    tester.show()
    app.exec()
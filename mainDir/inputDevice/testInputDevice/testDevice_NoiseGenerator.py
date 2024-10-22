from PyQt6.QtWidgets import QApplication

from mainDir.inputDevice.testInputDevice.baseTestDevice_InputDevice import InputDeviceAppTester
from mainDir.inputDevice.generatorDevice.inputDevice_noiseGenerator import InputDevice_NoiseGenerator

if __name__ == "__main__":
    app = QApplication([])
    tester = InputDeviceAppTester(InputDevice_NoiseGenerator("Noise Generator"))
    tester.show()
    app.exec()
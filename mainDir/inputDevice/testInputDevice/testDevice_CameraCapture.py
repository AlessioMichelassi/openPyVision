import atexit
import cProfile
import io
import pstats
import threading

from PyQt6.QtWidgets import QApplication

from mainDir.inputDevice.captureDevice.inputDevice_cameraCapture import InputDevice_CameraCapture
from mainDir.inputDevice.testInputDevice.baseTestDevice_InputDevice import InputDeviceAppTester

def main():
    app = QApplication([])
    tester = InputDeviceAppTester(InputDevice_CameraCapture("Camera Capture"))
    tester.show()
    app.exec()


if __name__ == "__main__":
    pr = cProfile.Profile()
    pr.enable()


    def exit_handler():
        print("Thread attivi alla chiusura:", threading.enumerate())
        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats(26)
        print(s.getvalue())


    atexit.register(exit_handler)
    main()

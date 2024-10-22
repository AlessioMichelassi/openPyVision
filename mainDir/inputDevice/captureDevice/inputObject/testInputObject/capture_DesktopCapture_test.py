import sys
import cProfile
import pstats
import io

import cv2
from PyQt6.QtCore import QTimer

from mainDir.inputDevice.baseDevice.baseClass.baseTest_videoApp import VideoApp
from mainDir.inputDevice.captureDevice.inputObject.desktopCapture import DesktopCapture


def testDesktopCapture():
    capture_input = DesktopCapture(None)
    capture_input.initCamera(0)
    app = VideoApp(sys.argv, capture_input)
    app.exec()




def main():
    testDesktopCapture()
    QTimer.singleShot(2000, sys.exit)



if __name__ == "__main__":
    pr = cProfile.Profile()
    pr.enable()
    main()
    pr.disable()
    s = io.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats(30)
    print(s.getvalue())

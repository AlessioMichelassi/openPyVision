import json
import sys
import cProfile
import pstats
import io

import cv2
from PyQt6.QtCore import QTimer

from mainDir.inputDevice.baseDevice.baseClass.baseTest_videoApp import VideoApp
from mainDir.inputDevice.captureDevice.inputObject.videoCapture017 import VideoCapture017


def testVMixOutCapture():
    """
    This test work great with vMixOut
    :return:
    """
    capture_input = VideoCapture017(None)
    dictionary = capture_input.getDeviceDictionary()
    capture_input.initCamera(3)
    print(json.dumps(dictionary, indent=4))
    app = VideoApp(sys.argv, capture_input)
    app.exec()


def testUSBCameraCaptureCapture():
    """
    This test work great with USbCamera
    :return:
    """
    capture_input = VideoCapture017()
    dictionary = capture_input.getDeviceDictionary()
    capture_input.initCamera(1, api=cv2.CAP_DSHOW)
    capture_input.showHiddenSettings()
    print(json.dumps(dictionary, indent=4))
    app = VideoApp(sys.argv, capture_input)
    app.exec()


def testDeckLinkCaptureCapture(index=0):
    """
    This test work great with USbCamera
    :return:
    """
    capture_input = VideoCapture017()
    dictionary = capture_input.getDeviceDictionary()
    capture_input.initCamera(index, cv2.CAP_DSHOW)
    capture_input.set_camera_properties()
    capture_input.showHiddenSettings()
    print(json.dumps(dictionary, indent=4))
    app = VideoApp(sys.argv, capture_input)
    app.exec()



def main():
    testDeckLinkCaptureCapture(0)
    QTimer.singleShot(100, sys.exit)



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

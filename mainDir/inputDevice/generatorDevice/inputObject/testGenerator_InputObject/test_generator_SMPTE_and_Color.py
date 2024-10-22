import sys
import cProfile
import pstats
import io

from PyQt6.QtCore import QTimer

from mainDir.inputDevice.baseDevice.baseClass.baseTest_videoApp import VideoApp
from mainDir.inputDevice.generatorDevice.inputObject.generator_Color import ColorGenerator

from mainDir.inputDevice.generatorDevice.inputObject.generator_SMPTE import SMPTEBarsGenerator


def testSMPTEBarsGenerator():
    generator_input = SMPTEBarsGenerator()
    app = VideoApp(sys.argv, generator_input)
    app.exec()

def testRandomColorGenerator():
    generator_input = ColorGenerator()
    app = VideoApp(sys.argv, generator_input)
    app.exec()

def testColorGenerator():
    generator_input = ColorGenerator()
    generator_input.setColor({"red": 255, "green": 0, "blue": 0})
    app = VideoApp(sys.argv, generator_input)
    app.exec()


def main():
    testSMPTEBarsGenerator()
    QTimer.singleShot(200, sys.exit)
    testRandomColorGenerator()
    QTimer.singleShot(200, sys.exit)
    testColorGenerator()
    QTimer.singleShot(200, sys.exit)



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

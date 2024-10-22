import sys
import cProfile
import pstats
import io

from PyQt6.QtCore import QTimer

from mainDir.inputDevice.baseDevice.baseClass.baseTest_videoApp import VideoApp
from mainDir.inputDevice.playerDevice.inputObject.player_StillImage import StillImagePlayer


def testImagePlayer():
    path = r"/mainDir/imgs/testImage/testImg.png"
    noise_input = StillImagePlayer(path)
    app = VideoApp(sys.argv, noise_input)
    app.exec()




def main():
    testImagePlayer()
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

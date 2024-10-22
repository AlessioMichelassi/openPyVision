import sys
import cProfile
import pstats
import io

from PyQt6.QtCore import QTimer

from mainDir.inputDevice.baseDevice.baseClass.baseTest_videoApp import VideoApp
from mainDir.inputDevice.generatorDevice.inputObject.generator_Noise_Gaussian import GaussianNoiseGenerator
from mainDir.inputDevice.generatorDevice.inputObject.generator_Noise_Grain import GrainGenerator
from mainDir.inputDevice.generatorDevice.inputObject.generator_Noise_Random import RandomNoiseGenerator
from mainDir.inputDevice.generatorDevice.inputObject.generator_Noise_SaltAndPepper import SaltAndPepperGenerator


def testRandomNoiseGenerator():
    noise_input = RandomNoiseGenerator()
    app = VideoApp(sys.argv, noise_input)
    app.exec()


def testGaussianNoiseGenerator():
    noise_input = GaussianNoiseGenerator()
    app = VideoApp(sys.argv, noise_input)
    app.exec()


def SaltAndPepperNoiseGenerator():
    # Inizializza l'input specifico
    noise_input = SaltAndPepperGenerator()
    app = VideoApp(sys.argv, noise_input)
    app.exec()

def testGrainGenerator():
    noise_input = GrainGenerator()
    app = VideoApp(sys.argv, noise_input)
    app.exec()


def main():
    testGaussianNoiseGenerator()
    # testRandomNoiseGenerator()
    # QTimer.singleShot(10, sys.exit)
    testGrainGenerator()
    QTimer.singleShot(2000, sys.exit)
    SaltAndPepperNoiseGenerator()
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

import logging

import numpy as np
from PyQt6.QtCore import QSize

from mainDir.inputDevice.baseDevice.baseClass.baseClass_InputObject import InputObject_BaseClass
from mainDir.errorClass.loggerClass import error_logger


class ColorGenerator(InputObject_BaseClass):

    @error_logger.log(log_level=logging.DEBUG)
    def __init__(self, resolution=QSize(1920, 1080)):
        super().__init__(resolution)
        self._name = self.__class__.__name__
        self.resolution = resolution
        self._frame = np.zeros((resolution.height(), resolution.width(), 3), dtype=np.uint8)
        self.color = self.generateRandomColor()
        self.setColor(self.color)

    @error_logger.log(log_level=logging.DEBUG)
    def setColor(self, data: dict):
        print(f"Setting color: {data}")
        if isinstance(data, dict):
            red = data.get('red', 0)
            green = data.get('green', 0)
            blue = data.get('blue', 0)
            self.color = {'red': red, 'green': green, 'blue': blue}
            self._frame[:, :] = [blue, green, red]
        elif isinstance(data, tuple):
            red, green, blue = data
            self.color = {'red': red, 'green': green, 'blue': blue}
            self._frame[:, :] = [blue, green, red]
        else:
            print(f"Error setting color: {data}")


    @error_logger.log(log_level=logging.DEBUG)
    def generateRandomColor(self):
        # Genera un colore casuale come un dizionario con chiavi 'red', 'green', 'blue'
        return {
            'red': int(np.random.randint(0, 255)),
            'green': int(np.random.randint(0, 255)),
            'blue': int(np.random.randint(0, 255))
        }


    def captureFrame(self):
        super().updateFps()

    @error_logger.log(log_level=logging.DEBUG)
    def serialize(self):
        # Chiama il metodo serialize della classe base
        base_data = super().serialize()
        base_data.update({
            'color': self.color  # Ora 'color' è un dizionario, quindi serializzabile
        })
        return base_data

    @error_logger.log(log_level=logging.DEBUG)
    def deserialize(self, data):
        # Chiama il metodo deserialize della classe base
        super().deserialize(data)
        # Estrai e imposta i dati specifici di ColorGenerator
        self.color = data.get('color',
                              {'red': 255, 'green': 0, 'blue': 0})  # Imposta un colore di default se non trovato
        self.setColor(self.color)

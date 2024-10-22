
import time
import cv2
import numpy as np
from PyQt6.QtCore import QObject, QSize




class InputObject_BaseClass(QObject):
    """
       InputObject_BaseClass is the base class for all input objects.
         It provides the basic functionality for capturing, processing and getting the frames.

       """

    
    def __init__(self, resolution=QSize(1920, 1080)):
        super().__init__()
        self._name = self.__class__.__name__
        self.resolution = resolution
        self._frame = np.zeros((resolution.height(), resolution.width(), 3), dtype=np.uint8)
        self.start_time = time.time()
        self.frame_count = 0
        self.total_time = 0
        self.fps = 0
        self.last_update_time = time.time()

    def captureFrame(self):
        """
        This is a base function for all inputObjects. It should be implemented in the derived classes.
        So, for example, a camera input object should capture a frame from the camera, while a generator
        like a noise generator should generate a frame. You can put here the code here after super().captureFrame()
        in order to get the updated frame.
        :return:
        """
        self.updateFps()


    def getFrame(self):
        """
        Returns the current frame.
        This is the second base function for all inputObjects. The generated or captured frame is always put in
        the _frame variable. With the getFrame you can get the last frame.
        :return:
        """
        return self._frame


    def getFps(self):
        """
        Returns the current FPS.
        :return:
        """
        return self.fps


    def updateFps(self):
        """
        Updates the FPS counter.
        If you process the image you probably need to know if there is a bottleneck in the processing.
        This function updates the FPS counter. it slows down in case of heavy processing.
        :return:
        """
        self.frame_count += 1
        current_time = time.time()
        elapsed_time = current_time - self.last_update_time
        if elapsed_time >= 1.0:  # Update FPS every second
            self.fps = self.frame_count / elapsed_time
            self.frame_count = 0
            self.last_update_time = current_time


    def serialize(self):
        return {
            "name": self._name,
            "resolution": [self.resolution.width(), self.resolution.height()],
        }

    def deserialize(self, data):
        try:
            self.resolution = QSize(data["resolution"][0], data["resolution"][1])
        except KeyError as e:
            print(f"Error deserializing data: {e}\n data was: {data}")

    def setParams(self, params):
        """
        Set the parameters of the input object.
        :param params:
        :return:
        """
        pass

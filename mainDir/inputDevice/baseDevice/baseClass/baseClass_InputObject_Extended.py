import logging
import time
from functools import wraps

import cv2
import numpy as np
from PyQt6.QtCore import QObject, QSize

from mainDir.errorClass.loggerClass import ErrorClass
from mainDir.outputs.openGLViewer015 import error_logger


class InputObject_BaseClass_Extender(QObject):
    """
       InputObject_BaseClass is the base class for all input objects.
         It provides the basic functionality for capturing, processing and getting the frames.

       Attributes:
           clip_limit (float): Il limite massimo di contrasto per CLAHE.
           tile_grid_size (tuple): La dimensione della griglia per CLAHE.
           gamma (float): Il valore di correzione gamma da applicare.
           isFrameInverted (bool): Se il frame deve essere invertito.
           isFrameAutoScreen (bool): Se applicare l'effetto auto screen.
           isFrameCLAHE (bool): Se applicare il CLAHE.
           isFrameHistogramEqualization (bool): Se applicare l'equalizzazione dell'istogramma.
           isFrameCLAHEYUV (bool): Se applicare il CLAHE sul canale YUV.
           isFrameHistogramEqualizationYUV (bool): Se applicare l'equalizzazione dell'istogramma sul canale YUV.
       """
    clip_limit = 2.0
    tile_grid_size = (4, 4)
    gamma = 1.0
    isFrameInverted = False
    isFrameAutoScreen = False
    isFrameCLAHE = False
    isFrameHistogramEqualization = False
    isFrameCLAHEYUV = False
    isFrameHistogramEqualizationYUV = False

    @error_logger.log(log_level=logging.DEBUG)
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
        return self.frameProcessor(self._frame)


    def getFps(self):
        """
        Returns the current FPS.
        :return:
        """
        return self.fps


    def frameProcessor(self, frame):
        """
        This function process the frame with the enabled effects.
        :param frame:
        :return:
        """
        if self.isFrameInverted:
            frame = self.invertFrame(frame)
        if self.isFrameAutoScreen:
            frame = self.autoScreenFrame(frame)
        if self.isFrameCLAHE:
            frame = self.applyCLAHE(frame, self.clip_limit, self.tile_grid_size)
        if self.isFrameHistogramEqualization:
            frame = self.applyHistogramEqualization(frame)
        if self.isFrameCLAHEYUV:
            frame = self.applyCLAHEYUV(frame, self.clip_limit, self.tile_grid_size)
        if self.isFrameHistogramEqualizationYUV:
            frame = self.applyHistogramEqualizationYUV(frame)
        if self.gamma != 1.0:
            frame = self.applyGammaByLut(frame, self.gamma)
        return frame


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

    @ErrorClass().log(log_level=logging.DEBUG)
    def invertFrame(self, image):
        """
        Inverts the frame colors.
        """
        return cv2.bitwise_not(image)

    @ErrorClass().log(log_level=logging.DEBUG)
    def autoScreenFrame(self, image):
        """
        Do a Screen Effect on the frame. Screen in compositing was an effect derived
        from the optical technique of exposing film with two images. The effect is created
        by exposing the film with two negative images, to a new positive print. The effect
        is characterized by the light areas in the two images adding together to become
        lighter, while the dark areas add together to become darker.
        Doing this with the same image can give a boost to the middle tones resulting in a
        brighter image.
        """
        inv1 = cv2.bitwise_not(image)
        mult = cv2.multiply(inv1, inv1, scale=1.0 / 255.0)
        return cv2.bitwise_not(mult).astype(np.uint8)

    @ErrorClass().log(log_level=logging.DEBUG)
    def getRGBChannels(self, frame):
        """
        Returns a tuple of 3 matrices (r, g, b) from the image.
        """
        return cv2.split(frame)

    @ErrorClass().log(log_level=logging.DEBUG)
    def setRGBChannels(self, channels):
        """
        Merge tre matrix rgb o bgr into a single image.
        channels: tuple of 3 matrices (r, g, b)
        """
        return cv2.merge(channels)

    @ErrorClass().log(log_level=logging.DEBUG)
    def applyGammaByLut(self, image, gamma):
        """
        Apply gamma correction using the lookup table method.
        This method is more efficient than using the pow function and take less time.
        :param image:
        :param gamma:
        :return:
        """
        inv_gamma = 1.0 / gamma
        table = np.array([(i / 255.0) ** inv_gamma * 255
                          for i in range(256)]).astype(np.uint8)
        return cv2.LUT(image, table)

    @ErrorClass().log(log_level=logging.DEBUG)
    def applyCLAHE(self, image, clip_limit=2.0, tile_grid_size=(8, 8)):
        """
        Applies the Contrast Limited Adaptive Histogram Equalization (CLAHE) to the image.

        Parameters:
            image (numpy.ndarray): The input frame to process.
            clip_limit (float): The contrast limit for CLAHE. Default is 2.0.
            tile_grid_size (tuple): The size of the grid for CLAHE. Default is (8, 8).

        Returns:
            numpy.ndarray: The image with CLAHE applied.
    """
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        return clahe.apply(image)

    @ErrorClass().log(log_level=logging.DEBUG)
    def applyHistogramEqualization(self, image):
        """
        Applies the Histogram Equalization to the image.
        """
        return cv2.equalizeHist(image)

    @ErrorClass().log(log_level=logging.DEBUG)
    def applyCLAHEYUV(self, image, clip_limit=2.0, tile_grid_size=(8, 8)):
        """
        Applies the Contrast Limited Adaptive Histogram Equalization (CLAHE) to the Y channel of the YUV image.
        """
        yuv_img = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        yuv_img[:, :, 0] = clahe.apply(yuv_img[:, :, 0])
        return cv2.cvtColor(yuv_img, cv2.COLOR_YUV2BGR)

    @ErrorClass().log(log_level=logging.DEBUG)
    def applyHistogramEqualizationYUV(self, image):
        """
        Applies the Histogram Equalization to the Y channel of the YUV image.
        """
        yuv_img = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
        yuv_img[:, :, 0] = cv2.equalizeHist(yuv_img[:, :, 0])
        return cv2.cvtColor(yuv_img, cv2.COLOR_YUV2BGR)

    @ErrorClass().log(log_level=logging.DEBUG)
    def setParams(self, params):
        """
        Set the parameters of the input object.
        :param params:
        :return:
        """
        pass

    @ErrorClass().log(log_level=logging.DEBUG)
    def serialize(self):
        return {
            "name": self._name,
            "resolution": [self.resolution.width(), self.resolution.height()],
            "isFrameInverted": self.isFrameInverted,
            "isFrameAutoScreen": self.isFrameAutoScreen,
            "isFrameCLAHE": self.isFrameCLAHE,
            "isFrameHistogramEqualization": self.isFrameHistogramEqualization,
            "isFrameCLAHEYUV": self.isFrameCLAHEYUV,
            "isFrameHistogramEqualizationYUV": self.isFrameHistogramEqualizationYUV,
            "gamma": self.gamma
        }

    @ErrorClass().log(log_level=logging.DEBUG)
    def deserialize(self, data):
        try:
            self.resolution = QSize(data["resolution"][0], data["resolution"][1])
            self.isFrameInverted = data["isFrameInverted"]
            self.isFrameAutoScreen = data["isFrameAutoScreen"]
            self.isFrameCLAHE = data["isFrameCLAHE"]
            self.isFrameHistogramEqualization = data["isFrameHistogramEqualization"]
            self.isFrameCLAHEYUV = data["isFrameCLAHEYUV"]
            self.isFrameHistogramEqualizationYUV = data["isFrameHistogramEqualizationYUV"]
            self.gamma = data["gamma"]
        except KeyError as e:
            logging.error(f"Error deserializing data: Missing key {e}")
            print(f"Error deserializing data: {e}\n data was: {data}")

    @ErrorClass().log(log_level=logging.DEBUG)
    def setParams(self, params):
        """
        Set the parameters of the input object.
        :param params:
        :return:
        """
        pass

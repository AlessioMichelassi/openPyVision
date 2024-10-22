import logging
import cv2
import numpy as np
import dxcam
from PyQt6.QtCore import *

from mainDir.inputDevice.baseDevice.baseClass.baseClass_InputObject import InputObject_BaseClass
from mainDir.errorClass.loggerClass import error_logger


class DesktopCapture(InputObject_BaseClass):

    @error_logger.log(log_level=logging.DEBUG)
    def __init__(self, screen_index=None, screen_region=None, resolution=QSize(1920, 1080)):
        super().__init__(resolution)
        self._name = self.__class__.__name__
        self.camera = None
        self.screenRegion = screen_region if screen_region else (0, 0, resolution.width(), resolution.height())
        self._frame = np.zeros((resolution.height(), resolution.width(), 3), dtype=np.uint8)
        self.needs_resize = False
        if screen_index is not None:
            self.screenIndex = screen_index
            self.initCamera(screen_index)

    @error_logger.log(log_level=logging.DEBUG)
    def initCamera(self, screen_index):
        """Initializes the camera for screen capture."""
        print("Initializing camera")
        self.release()  # Ensure no previous camera is running
        self.screenIndex = screen_index
        try:
            screens = dxcam.device_info()
            if screen_index >= len(screens):
                logging.error(f"Screen index {screen_index} out of range. Available screens: {len(screens)}")
                return

            logging.info(f"Initializing screen capture for screen index {screen_index}. Available screens: {screens}")
            self.camera = dxcam.create(
                output_idx=screen_index, output_color="BGR",
                max_buffer_len=16, region=self.screenRegion
            )
            self.camera.start(target_fps=60, video_mode=True)
            logging.info(f"Camera initialized for screen index {screen_index}")
        except Exception as e:
            logging.error(f"Failed to open screen source {screen_index}: {e}")
            self.camera = None

    @error_logger.log(log_level=logging.DEBUG)
    def release(self):
        """Stops the camera capture and releases the resources."""
        if self.camera:
            logging.info(f"Releasing screen capture for screen index {self.screenIndex}")
            self.camera.stop()
            self.camera = None
        else:
            logging.debug("Camera was not initialized, nothing to release.")

    @error_logger.log(log_level=logging.DEBUG)
    def captureFrame(self):
        """Captures a frame from the screen capture."""
        super().captureFrame()
        if self.camera:
            frame = self.camera.get_latest_frame()
            if frame is not None:
                self._frame = self.resizeFrame(frame) if self.needs_resize else frame
                self.updateFps()
                # logging.debug(f"Captured frame for screen {self.screenIndex}")
            else:
                logging.warning(f"No frame captured from screen {self.screenIndex}")
        else:
            logging.error("Camera is not initialized.")

    @error_logger.log(log_level=logging.DEBUG)
    def resizeFrame(self, frame):
        """Resizes the frame to match the expected resolution."""
        logging.info(f"Resizing frame for screen {self.screenIndex}")
        return cv2.resize(frame, (self.resolution.width(), self.resolution.height()), interpolation=cv2.INTER_LINEAR)

    @error_logger.log(log_level=logging.DEBUG)
    def checkSize(self):
        """Checks if the captured frame size matches the expected resolution."""
        if self.camera:
            frame = self.camera.get_latest_frame()
            if frame is not None and (frame.shape[1], frame.shape[0]) != (
                    self.resolution.width(), self.resolution.height()):
                logging.info(f"Resizing is needed for screen {self.screenIndex}")
                self.needs_resize = True
            else:
                logging.info(f"No resizing needed for screen {self.screenIndex}")
        else:
            logging.error("Cannot check size because the camera is not initialized.")

    @error_logger.log(log_level=logging.DEBUG)
    def serialize(self):
        """Serializes the current state of the object."""
        base_data = super().serialize()
        base_data.update({
            'screenIndex': self.screenIndex,
            'screenRegion': self.screenRegion,
        })
        logging.info(f"Serialized data for screen {self.screenIndex}")
        return base_data

    @error_logger.log(log_level=logging.DEBUG)
    def deserialize(self, data):
        """Deserializes the state of the object."""
        super().deserialize(data)
        self.screenIndex = data.get('screenIndex', self.screenIndex)
        self.screenRegion = data.get('screenRegion', self.screenRegion)
        self.initCamera(self.screenIndex)
        logging.info(f"Deserialized data and reinitialized camera for screen {self.screenIndex}")

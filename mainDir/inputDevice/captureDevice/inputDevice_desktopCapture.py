import logging

from PyQt6.QtCore import *
from PyQt6.QtGui import *

from mainDir.inputDevice.baseDevice.inputDevice_Base import InputDevice_BaseClass
from mainDir.inputDevice.captureDevice.captureWidget.desktopCaptureWidget import DesktopCaptureWidget
from mainDir.inputDevice.captureDevice.inputObject.desktopCapture import DesktopCapture


class InputDevice_DesktopCapture(InputDevice_BaseClass):
    """
        An InputDevice is any input of the mixer.
        It put together the thread, the input object and the graphic interface
        and act as interface to the mixer
        """

    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.active = False
        self.graphicInterface = DesktopCaptureWidget()
        # Connect the parametersChanged signal from the widget to handle updates
        self.graphicInterface.typeChanged.connect(self.onTypeChanged)
        self.graphicInterface.paramsChanged.connect(self.onParamsChanged)
        self.currentInputType = 0
        self.currentParams = {
            "screenRegion": (0, 0, 1920, 1080)
        }
        self.inputObject = None  # Inizialmente l'inputObject è None


    def onTypeChanged(self, data):
        currentTypeName = data.get('type')
        currentTypeIndex = data.get('index')
        if not currentTypeIndex:
            currentTypeIndex = 0

        print(f"*** inputDevice: Device Changed to {currentTypeName} {currentTypeIndex} ***")
        self.currentInputType = currentTypeIndex
        if self.inputObject:
            print("*** *** inputDevice: Stopping previous input object ***")
            self.inputObject.release()
        print("****** inputDevice: Creating new input object ***")
        print(f"*** inputDevice: Creating input object for device '{currentTypeName}'")
        self.inputObject = DesktopCapture(screen_index=currentTypeIndex,
                                            screen_region=self.currentParams["screenRegion"])
        self.inputObject.initCamera(currentTypeIndex)
        self.setInputObject(self.inputObject)
        print(f"*** inputDevice: Input object for device '{currentTypeName}' created successfully.")

    def onParamsChanged(self, data):
        pass

    def serialize(self):
        """
        Serializes the current state of the input device (Noise generator) into a dictionary.
        """
        data = super().serialize()  # Call the base class method
        data.update({
            "name": self._name,
            "type": "DesktopCapture",
            "params": self.currentParams
        })

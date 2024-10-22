import cv2

from mainDir.inputDevice.baseDevice.inputDevice_Base import InputDevice_BaseClass
from mainDir.inputDevice.captureDevice.captureWidget.captureWidget_camera import CaptureWidget_Camera
from mainDir.inputDevice.captureDevice.inputObject.videoCapture017 import VideoCapture017


class InputDevice_CameraCapture(InputDevice_BaseClass):
    """
        An InputDevice is any input of the mixer.
        It put together the thread, the input object and the graphic interface
        and act as interface to the mixer
        """

    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.active = False
        self.graphicInterface = CaptureWidget_Camera()
        # Connect the parametersChanged signal from the widget to handle updates
        self.graphicInterface.typeChanged.connect(self.onTypeChanged)
        self.graphicInterface.paramsChanged.connect(self.onParamsChanged)
        self.currentInputType = 0
        self.currentParams = {}
        self.inputObject = None  # Inizialmente l'inputObject è None

    def onTypeChanged(self, data):
        currentTypeName = data.get('type')
        currentTypeIndex = data.get('index')
        if currentTypeIndex:
            print(f"*** Device Changed to {currentTypeName} {currentTypeIndex} ***")
            self.currentInputType = currentTypeIndex
            self.currentParams = {}
            api = self.checkApi(currentTypeName)
            # Crea l'inputObject solo dopo che l'utente ha selezionato un dispositivo
            if self.inputObject:
                self.inputObject.stop()  # Ferma il precedente inputObject se esiste
            print("*** Creating new input object ***")
            print(f"Creating input object for device '{currentTypeName}'")
            print(f"API: {api}")
            self.inputObject = VideoCapture017(cameraIndex=currentTypeIndex, api=api)
            self.setInputObject(self.inputObject)
            print(f"Input object for device '{currentTypeName}' created successfully.")
        else:
            print("No device selected.")

    def checkApi(self, deviceName):
        # Verifica se uno dei termini "Blackmagic", "Decklink" o "WDM" è nel nome del dispositivo
        if any(keyword in deviceName for keyword in ["Blackmagic", "Decklink", "WDM"]):
            print(f"Device '{deviceName}' is a capture card. Using CAP_DSHOW API.")
            return cv2.CAP_DSHOW
        else:
            print(f"Device '{deviceName}' is not a capture card. Using CAP_MSMF API.")
            return cv2.CAP_ANY

    def onParamsChanged(self, data):
        self._input_object.showHiddenSettings()

    def serialize(self):
        """
        Serializes the current state of the input device (Noise generator) into a dictionary.
        """
        data = super().serialize()  # Call the base class method
        data.update({
            "name": self._name,
            "type": self.currentInputType,
            "params": self.currentParams
        })

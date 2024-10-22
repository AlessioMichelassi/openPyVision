import json
import sys

import cv2
import numpy as np
from PyQt6.QtCore import *

from mainDir.inputDevice.baseDevice.baseClass.baseClass_InputObject import InputObject_BaseClass
from mainDir.inputDevice.baseDevice.baseClass.baseTest_videoApp import VideoApp
from mainDir.inputDevice.captureDevice.inputObject.deviceFinder.deviceUpdater import DeviceUpdater

"""
La classe VideoCapture è una sottoclasse di BaseClass e rappresenta un'entità che cattura i frame da una sorgente video
usa la libreria OpenCV per catturare i frame da una webcam o da una scheda di acquisizione. OpenCV non ha un sistema per
ottenere il nome della periferica, quindi si usa ffmpeg per ottenere le informazioni sui dispositivi. Queste informazioni 
vengono reperite usando la classe DeviceUpdater, che è un thread che esegue un comando ffmpeg per ottenere le informazioni
sui dispositivi audio e video disponibili. Se il dispositivo è noto, perchè ad esempio è stato già selezionato da una combo
box, tipo quella di matrixWidget si può passare il dizionario altrimenti il dizionario viene calcolato automaticamente.

Il dizionario serve per sapere se il dispositivo è una webcam o una scheda di acquisizione. Mentre il dispositivo di 
acquisizione ha generalmente un'interfaccia grafica creata dal produttore per impostare i parametri di acquisizione,
la web cam non li ha. Se la webcam è un pò datata, potrebbe fra l'altro non supportare l'acquisizione con con driver
diversi da DShow (quindi non ha una latenza ottimizzata). In alternativa si può usare forceDShow=True per forzare l'uso 
di Dshow e saltare la ricerca dei dispositivi.


"""


class VideoCapture017(InputObject_BaseClass):
    needResizing = False

    
    def __init__(self, cameraIndex=None, api=None, resolution=QSize(1920, 1080)):
        super().__init__(resolution)
        self.cameraIndex = cameraIndex
        self.target_resolution = (resolution.height(), resolution.width())
        self._frame = np.zeros((resolution.height(), resolution.width(), 3), dtype=np.uint8)
        self.camera = None
        self.api = api
        if self.cameraIndex is not None:
            if self.api is None:
                self.initCamera(self.cameraIndex)
            else:
                self.initCamera(self.cameraIndex, self.api)

    def initCamera(self, deviceIndex, api=cv2.CAP_DSHOW):
        device_string = f'video={deviceIndex}'
        print(f"Initializing camera with device string: {deviceIndex}")
        self.camera = cv2.VideoCapture(deviceIndex, api)
        if not self.camera.isOpened():
            print(f"Failed to open camera with device string: {deviceIndex}")
        else:
            print(f"Camera opened successfully with device string: {deviceIndex}")
            self.set_camera_properties()

    
    def getDeviceDictionary(self):
        return self.devices_dictionary

    def updateDevicesDictionary(self, devices):
        """
        Aggiorna il dizionario dei dispositivi con le informazioni ottenute da ffmpeg.
        In base all'indice della camera, si può personalizzare alcuni aspetti della cattura video.
        Le camere USB ad esempio, potrebbero avere un nome che contiene la parola "webcam" e quindi si può forzare
        l'uso di DShow per ottenere una latenza minore, mentre le schede di acquisizione Decklink potrebbero avere
        un nome che contiene la parola "Decklink" e quindi si può forzare l'uso di ffmpeg per ottenere una latenza
        minore.
        :param devices:
        :return:
        """
        print(f"Devices: {json.dumps(devices, indent=4)}")
        self.devices_dictionary = devices


    def showHiddenSettings(self):
        self.camera.set(cv2.CAP_PROP_SETTINGS, 1)

    def openDefaultSettingsInterface(self):
        self.camera.set(cv2.CAP_PROP_SETTINGS, 1)

    def set_camera_properties(self):
        if not self.camera:
            print("Camera is not initialized.")
            return
        if self.api == cv2.CAP_DSHOW:
            success = True
            # Set the frame width and height
            width_set = self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.target_resolution[1])
            height_set = self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.target_resolution[0])
            fps_set = self.camera.set(cv2.CAP_PROP_FPS, 60)

            if not width_set or not height_set or not fps_set:
                print("Failed to set one or more camera properties")
                success = False
            else:
                actual_width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
                actual_height = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
                actual_fps = self.camera.get(cv2.CAP_PROP_FPS)
                print(f"Camera resolution set to {actual_width}x{actual_height} at {actual_fps} FPS")

            if success:
                print("Camera properties set successfully.")

    def stop(self):
        if self.camera:
            self.camera.release()

    def captureFrame(self):
        super().captureFrame()
        # se la camera è aperta e inizializzata, leggi il frame
        if self.camera and self.camera.isOpened():
            ret, frame = self.camera.read()
            if not ret:
                print("Failed to read frame from camera")
                self._frame = self.returnBlackFrame()
                return
            # se il frame non è vuoto, ridimensiona il frame se necessario
            frame_height, frame_width = frame.shape[:2]
            if (frame_width, frame_height) != (self.target_resolution[1], self.target_resolution[0]):
                try:
                    self._frame = cv2.resize(frame, self.target_resolution, interpolation=cv2.INTER_AREA)
                except Exception as e:
                    print(f"Error resizing frame: {e}")
                    self._frame = frame
            else:
                # se non è necessario ridimensionare il frame, assegna il frame al frame attuale
                self._frame = frame
        else:
            #se non riesce a aprire la camera, assegna un frame nero
            print("Camera is not initialized.")
            self._frame = self.returnBlackFrame()

    def getFrame(self):
        return self._frame

    def returnBlackFrame(self):
        return np.zeros((self.target_resolution[0], self.target_resolution[1], 3), dtype=np.uint8)
    
    def serialize(self):
        base_data = super().serialize()
        base_data.update({
            'cameraIndex': self.cameraIndex,
            'deviceDictionary': self.devices_dictionary
        })
        return base_data

    def deserialize(self, data):
        super().deserialize(data)
        self.initCamera(self.cameraIndex)


# test class
if __name__ == '__main__':
    capture_input = VideoCapture017()
    capture_input.initCamera(11, api=cv2.CAP_ANY)
    capture_input.showHiddenSettings()
    app = VideoApp(sys.argv, capture_input)
    app.exec()
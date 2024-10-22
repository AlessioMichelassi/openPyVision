import logging
import random
import cv2
import numpy as np
from PyQt6.QtCore import *
import threading
from mainDir.inputDevice.baseDevice.baseClass.baseClass_InputObject import InputObject_BaseClass
from mainDir.errorClass.loggerClass import error_logger


class GrainGenerator(InputObject_BaseClass):

    @error_logger.log(log_level=logging.DEBUG)
    def __init__(self, resolution=QSize(1920, 1080)):
        super().__init__(resolution)
        self._name = self.__class__.__name__  # Nome della classe per identificare l'oggetto
        self.resolution = resolution  # Risoluzione del frame
        self._grain_size = 3  # Dimensione del grano del rumore
        self._r_speed = 2  # Velocità di scorrimento del canale rosso
        self._g_speed = 1  # Velocità di scorrimento del canale verde
        self._b_speed = 3  # Velocità di scorrimento del canale blu
        self._r_offset = 2  # Offset iniziale del canale rosso
        self._g_offset = 0  # Offset iniziale del canale verde
        self._b_offset = 4  # Offset iniziale del canale blu
        self._frame = np.zeros((resolution.height(), resolution.width(), 3), dtype=np.uint8)  # Frame iniziale vuoto
        # Il generatore è un po' lento, quindi genera 120 frame in anticipo
        self.num_frames = 60  # Numero di frame da pre-generare
        self.frames = []  # Lista per i frame pre-generati
        self.current_frame_index = 0  # Indice del frame corrente
        self.capture_counter = 0  # Contatore delle catture per determinare quando cambiare il frame
        self.update_interval = 5  # Cambia frame ogni 5 catture

        # Avvia un thread per generare i frame iniziali
        self.generate_initial_frames_thread = threading.Thread(target=self.generate_initial_frames, daemon=True)
        self.generate_initial_frames_thread.start()

    def generate_initial_frames(self):
        """
        Genera i frame iniziali di rumore granulare in un thread separato.
        """
        height, width = self.resolution.height(), self.resolution.width()
        for _ in range(self.num_frames):
            # Genera un frame di rumore granulare e aggiungilo alla lista dei frame
            noise_frame = self.generateNoise()
            self.frames.append(noise_frame)

    def captureFrame(self):
        """
        Sovrascrive la funzione captureFrame della classe base, mantenendo la funzionalità originale.
        """
        super().captureFrame()
        # Aggiorna il frame ogni 'update_interval' catture
        if self.capture_counter % self.update_interval == 0 and self.frames:
            # Seleziona un frame casuale dalla lista dei frame pre-generati
            self.current_frame_index = random.randint(0, len(self.frames) - 1)
            self._frame = self.frames[self.current_frame_index]
        self.capture_counter += 1  # Incrementa il contatore delle catture

    def generateNoise(self):
        """
        Genera un frame di rumore granulare.
        """
        height, width = self.resolution.height(), self.resolution.width()
        grain_shape = (height // self._grain_size, width // self._grain_size)

        # Genera rumore a una risoluzione più piccola
        noise = np.random.randint(10, 200, (grain_shape[0], grain_shape[1], 3), dtype=np.uint8)
        # Ridimensiona il rumore alla risoluzione desiderata
        noise = cv2.resize(noise, (width, height), interpolation=cv2.INTER_NEAREST)

        # Applica gli offset di scorrimento per i canali
        noise = np.roll(noise, self._r_offset, axis=1)  # Scorrimento del canale rosso
        noise = np.roll(noise, self._g_offset, axis=0)  # Scorrimento del canale verde
        self._r_offset = (self._r_offset + self._r_speed) % width
        self._g_offset = (self._g_offset + self._g_speed) % height

        return noise

    def update_frames_in_background(self):
        """
        Aggiorna i frame pre-generati in un thread separato.
        Questo metodo viene utilizzato quando vengono cambiati i parametri del generatore.
        """
        threading.Thread(target=self.generate_initial_frames, daemon=True).start()

    @error_logger.log(log_level=logging.DEBUG)
    def setGrainSize(self, grain_size):
        self._grain_size = grain_size
        # Aggiorna i frame dopo il cambiamento del parametro
        self.update_frames_in_background()

    @error_logger.log(log_level=logging.DEBUG)
    def setRSpeed(self, r_speed):
        self._r_speed = r_speed
        # Aggiorna i frame dopo il cambiamento del parametro
        self.update_frames_in_background()

    @error_logger.log(log_level=logging.DEBUG)
    def setGSpeed(self, g_speed):
        self._g_speed = g_speed
        # Aggiorna i frame dopo il cambiamento del parametro
        self.update_frames_in_background()

    @error_logger.log(log_level=logging.DEBUG)
    def setBSpeed(self, b_speed):
        self._b_speed = b_speed
        # Aggiorna i frame dopo il cambiamento del parametro
        self.update_frames_in_background()

    @error_logger.log(log_level=logging.DEBUG)
    def setROffset(self, r_offset):
        self._r_offset = r_offset
        # Aggiorna i frame dopo il cambiamento del parametro
        self.update_frames_in_background()

    @error_logger.log(log_level=logging.DEBUG)
    def setGOffset(self, g_offset):
        self._g_offset = g_offset
        # Aggiorna i frame dopo il cambiamento del parametro
        self.update_frames_in_background()

    @error_logger.log(log_level=logging.DEBUG)
    def setBOffset(self, b_offset):
        self._b_offset = b_offset
        # Aggiorna i frame dopo il cambiamento del parametro
        self.update_frames_in_background()

    @error_logger.log(log_level=logging.DEBUG)
    def serialize(self):
        # Chiama il metodo serialize della classe base e aggiunge informazioni specifiche del GrainGenerator
        base_data = super().serialize()
        base_data.update({
            'grain_size': self._grain_size,
            'r_speed': self._r_speed,
            'g_speed': self._g_speed,
            'b_speed': self._b_speed,
            'r_offset': self._r_offset,
            'g_offset': self._g_offset,
            'b_offset': self._b_offset
        })
        return base_data

    @error_logger.log(log_level=logging.DEBUG)
    def deserialize(self, data):
        super().deserialize(data)
        if "params" in data:
            self.setParams(data["params"])

    def setParams(self, params):
        # Estrai e imposta i dati specifici di GrainGenerator
        self._grain_size = params.get('grain_size', 3)
        self._r_speed = params.get('r_speed', 2)
        self._g_speed = params.get('g_speed', 1)
        self._b_speed = params.get('b_speed', 3)
        self._r_offset = params.get('r_offset', 2)
        self._g_offset = params.get('g_offset', 0)
        self._b_offset = params.get('b_offset', 4)
        # Rigenera i frame iniziali in base ai dati deserializzati
        self.update_frames_in_background()
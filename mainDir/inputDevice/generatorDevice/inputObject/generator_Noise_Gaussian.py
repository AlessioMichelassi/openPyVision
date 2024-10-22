import logging
import random
import cv2
import numpy as np
from PyQt6.QtCore import *
import threading
from mainDir.inputDevice.baseDevice.baseClass.baseClass_InputObject_Extended import InputObject_BaseClass_Extender
from mainDir.errorClass.loggerClass import error_logger


class GaussianNoiseGenerator(InputObject_BaseClass_Extender):

    @error_logger.log(log_level=logging.DEBUG)
    def __init__(self, resolution=QSize(1920, 1080)):
        super().__init__(resolution)
        self._name = self.__class__.__name__  # Nome della classe per identificare l'oggetto
        self.resolution = resolution  # Risoluzione del frame
        self.num_frames = 120  # Numero di frame da pre-generare
        self.frames = []  # Lista per i frame pre-generati
        self.current_frame_index = 0  # Indice del frame corrente
        self.capture_counter = 0  # Contatore delle catture per determinare quando cambiare il frame
        self.update_interval = 5  # Cambia frame ogni 5 catture

        # Avvia un thread per generare i frame iniziali
        # Questo aiuta a evitare ritardi nell'inizializzazione principale
        self.generate_initial_frames_thread = threading.Thread(target=self.generate_initial_frames, daemon=True)
        self.generate_initial_frames_thread.start()

    def generate_initial_frames(self):
        """
        Genera i frame iniziali di rumore gaussiano in un thread separato.
        """
        height, width = self.resolution.height(), self.resolution.width()
        for _ in range(self.num_frames):
            # Genera un frame di rumore gaussiano e aggiungilo alla lista dei frame
            noise_frame = self.generate_gaussian_noise(height, width)
            self.frames.append(noise_frame)

    def captureFrame(self):
        """
        Sovrascrive la funzione captureFrame della classe base, mantenendo la funzionalità originale.
        """
        self.updateFps()  # Aggiorna il contatore di FPS per monitorare le prestazioni
        # Aggiorna il frame ogni 'update_interval' catture
        if self.capture_counter % self.update_interval == 0 and self.frames:
            # Seleziona un frame casuale dalla lista dei frame pre-generati
            self.current_frame_index = random.randint(0, len(self.frames) - 1)
            self._frame = self.frames[self.current_frame_index]
        self.capture_counter += 1  # Incrementa il contatore delle catture

    def generate_gaussian_noise(self, height, width):
        """
        Genera un frame di rumore gaussiano.
        """
        mean = 0  # Media del rumore gaussiano
        sigma = 25  # Deviazione standard del rumore gaussiano
        # Genera rumore gaussiano con media e deviazione standard specificate
        gaussian_noise = np.random.normal(mean, sigma, (height, width, 3)).astype(np.float32)

        # Normalizza il rumore per essere tra 0 e 255 e convertilo in uint8
        noise_normalized = cv2.normalize(gaussian_noise, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        return noise_normalized

    @error_logger.log(log_level=logging.DEBUG)
    def serialize(self):
        # Chiama il metodo serialize della classe base e aggiunge informazioni specifiche del GaussianNoiseGenerator
        base_data = super().serialize()
        base_data.update({
            'num_frames': self.num_frames,
            'update_interval': self.update_interval
        })
        return base_data

    @error_logger.log(log_level=logging.DEBUG)
    def deserialize(self, data):
        super().deserialize(data)
        # Estrai e imposta i dati specifici di GaussianNoiseGenerator
        self.num_frames = data.get('num_frames', 120)
        self.update_interval = data.get('update_interval', 5)
        # Rigenera i frame iniziali in base ai dati deserializzati
        self.frames = [self.generate_gaussian_noise(self.resolution.height(), self.resolution.width()) for _ in range(self.num_frames)]
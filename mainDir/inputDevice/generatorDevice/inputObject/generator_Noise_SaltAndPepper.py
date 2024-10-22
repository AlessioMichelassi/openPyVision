import random
import threading
import logging

import cv2
import numpy as np
from PyQt6.QtCore import *

from mainDir.inputDevice.baseDevice.baseClass.baseClass_InputObject import InputObject_BaseClass
from mainDir.errorClass.loggerClass import error_logger


class SaltAndPepperGenerator(InputObject_BaseClass):

    def __init__(self, resolution=QSize(1920, 1080)):
        super().__init__(resolution)
        self._name = self.__class__.__name__
        self.resolution = resolution
        self.salt_prob = 0.02
        self.pepper_prob = 0.03
        self._frame = np.zeros((resolution.height(), resolution.width(), 3), dtype=np.uint8)

        self.num_frames = 60
        self.frames = []  # Frame buffer attuale
        self.new_frames = []  # Frame buffer per la transizione
        self.current_frame_index = 0
        self.capture_counter = 0
        self.update_interval = 5

        # Avvia il thread per generare i frame iniziali
        self.generate_initial_frames_thread = threading.Thread(target=self.generate_initial_frames, daemon=True)
        self.generate_initial_frames_thread.start()

    def generate_initial_frames(self):
        """
        Genera i frame iniziali di rumore granulare in un thread separato.
        """
        height, width = self.resolution.height(), self.resolution.width()
        for _ in range(self.num_frames):
            noise_frame = self.generateNoise()
            self.frames.append(noise_frame)

    def update_frames_in_background(self):
        """
        Aggiorna i frame pre-generati in un thread separato con nuovi parametri.
        """
        threading.Thread(target=self.generate_new_frames, daemon=True).start()

    def generate_new_frames(self):
        """
        Genera nuovi frame con i parametri aggiornati e li mette nel buffer 'new_frames'.
        """
        height, width = self.resolution.height(), self.resolution.width()
        new_frames = []
        for _ in range(self.num_frames):
            noise_frame = self.generateNoise()
            new_frames.append(noise_frame)

        # Quando il nuovo buffer è pronto, sostituiscilo gradualmente
        self.new_frames = new_frames
        self.transition_frames()

    def transition_frames(self):
        """
        Sostituisce gradualmente i frame attuali con i nuovi frame usando l'interpolazione.
        """
        for i in range(len(self.frames)):
            if i < len(self.new_frames):
                # Interpolazione lineare tra i vecchi e i nuovi frame
                alpha = i / len(self.frames)
                self.frames[i] = cv2.addWeighted(self.frames[i], 1 - alpha, self.new_frames[i], alpha, 0)
        self.new_frames.clear()  # Svuota il buffer dei nuovi frame dopo la transizione

    def captureFrame(self):
        """
        Sovrascrive la funzione captureFrame della classe base, mantenendo la funzionalità originale.
        """
        super().captureFrame()
        if self.capture_counter % self.update_interval == 0 and self.frames:
            self.current_frame_index = random.randint(0, len(self.frames) - 1)
            self._frame = self.frames[self.current_frame_index]
        self.capture_counter += 1

    def generateNoise(self):
        height, width = self.resolution.height(), self.resolution.width()
        # Create a blank image with all pixels set to middle gray
        image = np.ones((height, width, 3), dtype=np.uint8) * 127

        # Add salt noise (white pixels)
        num_salt = np.ceil(self.salt_prob * height * width)
        coords = [np.random.randint(0, i - 1, int(num_salt)) for i in image.shape[:2]]
        image[coords[0], coords[1], :] = 255

        # Add pepper noise (black pixels)
        num_pepper = np.ceil(self.pepper_prob * height * width)
        coords = [np.random.randint(0, i - 1, int(num_pepper)) for i in image.shape[:2]]
        image[coords[0], coords[1], :] = 0

        return np.ascontiguousarray(image)

    def setSaltProbability(self, salt_prob):
        self.salt_prob = salt_prob
        self.update_frames_in_background()

    def setPepperProbability(self, pepper_prob):
        self.pepper_prob = pepper_prob
        self.update_frames_in_background()

    def serialize(self):
        # Chiama il metodo serialize della classe base
        base_data = super().serialize()
        base_data.update({
            'salt_probability': self.salt_prob,
            'pepper_probability': self.pepper_prob
        })
        return base_data

    def deserialize(self, data):
        # Chiama il metodo deserialize della classe base
        super().deserialize(data)
        if "params" in data:
            self.salt_prob = data["params"].get('salt_probability', 0.05)
            self.pepper_prob = data["params"].get('pepper_probability', 0.03)

    def setParams(self, params):
        # Estrai e imposta i dati specifici di SaltAndPepperGenerator
        print(f"SaltAndPepperGenerator.setParams: {params}")
        self.salt_prob = params.get('salt_probability', 0.05)
        self.pepper_prob = params.get('pepper_probability', 0.03)
        self.update_frames_in_background()
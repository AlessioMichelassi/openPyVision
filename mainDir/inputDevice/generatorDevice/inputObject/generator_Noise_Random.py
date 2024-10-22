import random
import threading

import cv2
import numpy as np


from PyQt6.QtCore import QSize
from mainDir.inputDevice.baseDevice.baseClass.baseClass_InputObject import InputObject_BaseClass


class RandomNoiseGenerator(InputObject_BaseClass):
    def __init__(self, resolution=QSize(1920, 1080)):
        super().__init__(resolution)
        self._name = self.__class__.__name__
        self.resolution = resolution
        self.running = True
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
            noise_frame = self.generateRandomNoise()
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


    def generateRandomNoise(self):
        """
        Genera un frame di rumore gaussiano.
        """
        height, width = self.resolution.height(), self.resolution.width()
        _frame = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
        return _frame

    def serialize(self):
        # Chiama il metodo serialize della classe base
        base_data = super().serialize()
        return base_data

    def deserialize(self, data):
        # Chiama il metodo deserialize della classe base
        super().deserialize(data)
        # Estrai e imposta i dati specifici di RandomNoiseGenerator
        pass


if __name__ == "__main__":
    generator = RandomNoiseGenerator()
    print("Generator started.")
    generator.captureFrame()
    frame = generator.getFrame()
    print(f"Frame generated with mean value: {np.mean(frame)}")


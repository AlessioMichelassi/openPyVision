import logging

import cv2
import numpy as np
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from mainDir.errorClass.loggerClass import ErrorClass
from mainDir.inputDevice.baseDevice.baseClass.baseClass_InputObject import InputObject_BaseClass


class InputObject_StingerPlayerForMixBus(InputObject_BaseClass):
    """
    Classe per gestire un'animazione Stinger all'interno del Mix Bus.

    Attributes:
        stingerPosition (int): Posizione del player all'interno del Mix Bus.
        index (int): L'indice corrente dell'animazione.
        lastIndex (int): L'ultimo indice usato per tenere traccia dell'avanzamento.
        isCached (bool): Flag per determinare se le immagini sono state salvate in cache.
        stingerPath (str): Percorso della cartella contenente le immagini dello Stinger.
        stingerInvAlphaImagesPath (str): Percorso delle immagini alpha inverse.
        stingerPreMultipliedImagesPath (str): Percorso delle immagini pre-moltiplicate.
        stingerPreMultipliedImages (list): Lista delle immagini pre-moltiplicate.
        stingerInvAlphaImages (list): Lista delle immagini alpha inverse.
    """

    @ErrorClass().log(log_level=logging.DEBUG)
    def __init__(self, params, position, resolution=QSize(1920, 1080)):
        """
        Inizializza la classe StingerPlayerForMixBus con le immagini pre-moltiplicate e inverse.

        Args:
            params (dict): Parametri di configurazione (deserializzati).
            position (int): Posizione del player all'interno del Mix Bus.
            resolution (QSize): Risoluzione del frame (default: 1920x1080).
        """
        super().__init__(resolution)
        self._name = self.__class__.__name__
        self.resolution = resolution
        self.stingerPosition = position
        self.index = 0
        self.lastIndex = 0
        self.isCached = False
        self.stingerPath = ""
        self.stingerInvAlphaImagesPath = ""
        self.stingerPreMultipliedImagesPath = ""
        self.stingerPreMultipliedImages = []
        self.stingerInvAlphaImages = []
        if params:
            self.deserialize(params)

    @ErrorClass().log(log_level=logging.INFO)
    def getFrames(self):
        """
        Restituisce i frame dell'animazione stinger.

        Returns:
            tuple: Frame alpha inverso e frame pre-moltiplicato.
        """
        if self.index > len(self.stingerPreMultipliedImages) -1:
            self.index = len(self.stingerPreMultipliedImages) - 1
        return self.stingerPreMultipliedImages[self.index], self.stingerInvAlphaImages[self.index]

    @ErrorClass().log(log_level=logging.INFO)
    def setStingerPremultipliedImages(self, images: list):
        """
        Imposta le immagini pre-moltiplicate dello stinger.

        Args:
            images (list): Lista delle immagini pre-moltiplicate.
        """
        self.stingerPreMultipliedImages = images

    @ErrorClass().log(log_level=logging.INFO)
    def setStingerInvAlphaImages(self, images: list):
        """
        Imposta le immagini alpha inverse dello stinger.

        Args:
            images (list): Lista delle immagini alpha inverse.
        """
        self.stingerInvAlphaImages = images

    @ErrorClass().log(log_level=logging.DEBUG)
    def captureFrame(self):
        """
        Sovrascrive la funzione `captureFrame` per tenere traccia dei frame catturati.
        """
        super().captureFrame()

    @ErrorClass().log(log_level=logging.INFO)
    def getLength(self):
        """
        Restituisce la lunghezza dell'animazione stinger.

        Returns:
            int: Numero totale di frame dell'animazione stinger.
        """
        return len(self.stingerPreMultipliedImages)

    @ErrorClass().log(log_level=logging.INFO)
    def setIndex(self, index):
        """
        Imposta l'indice corrente dell'animazione stinger.

        Args:
            index (int): Nuovo indice da impostare.
        """
        self.index = index

    @ErrorClass().log(log_level=logging.DEBUG)
    def getFrame(self):
        """
        Restituisce il frame corrente dell'animazione stinger.

        Returns:
            tuple: Frame alpha inverso e frame pre-moltiplicato.
        """
        if self.index < len(self.stingerPreMultipliedImages):
            invAFrame = self.stingerInvAlphaImages[self.index]
            preMultFrame = self.stingerPreMultipliedImages[self.index]
            return invAFrame, preMultFrame
        else:
            # Restituisce il primo frame se l'indice supera il numero totale di frame
            invAFrame = self.stingerInvAlphaImages[0]
            preMultFrame = self.stingerPreMultipliedImages[0]
            return invAFrame, preMultFrame

    @ErrorClass().log(log_level=logging.INFO)
    def serialize(self):
        """
        Serializza l'oggetto stinger player per la memorizzazione o il trasferimento.

        Returns:
            dict: Dati serializzati dell'oggetto stinger player.
        """
        base_data = super().serialize()
        base_data.update({
            'isCached': self.isCached,
            'stingerPosition': self.stingerPosition,
            'stingerFolder': self.stingerPath,
            'stingerInvAlphaImagesPath': self.stingerInvAlphaImagesPath,
            'stingerPreMultipliedImagesPath': self.stingerPreMultipliedImagesPath
        })
        return base_data

    @ErrorClass().log(log_level=logging.DEBUG)
    def deserialize(self, data):
        """
        Deserializza i dati dell'oggetto stinger player.

        Args:
            data (dict): Dati serializzati da deserializzare.
        """
        super().deserialize(data)
        self.isCached = data['isCached']
        self.stingerPath = data['stingerFolder']
        self.stingerPosition = data['stingerPosition']
        if self.isCached:
            self.stingerInvAlphaImagesPath = data['stingerInvAlphaImagesPath']
            self.stingerPreMultipliedImagesPath = data['stingerPreMultipliedImagesPath']

import numpy as np

from mainDir.inputDevice.baseDevice.inputDevice_Base import InputDevice_BaseClass
from mainDir.inputDevice.systemWidget.inputObject.inputObject_StingerPlayer import \
    InputObject_StingerPlayerForMixBus
from mainDir.inputDevice.systemWidget.stingerWidget.stingerLoaderWidget import StingerLoaderWidget


class InputDevice_StingerAnimation(InputDevice_BaseClass):
    """
        An InputDevice is any input of the mixer.
        It put together the thread, the input object and the graphic interface
        and act as interface to the mixer
    """

    def __init__(self, name, parent=None, stingerNumber=1):
        super().__init__(name, parent)
        self.active = False
        self.graphicInterface = StingerLoaderWidget(self, name, stingerNumber=stingerNumber)

    def getFrames(self):
        """
        Get the frames of the stinger animation.

        Returns:
            tuple: Pre-multiplied frame and inverse alpha frame.
        """
        if self._input_object:
            return self._input_object.getFrames()
        else:
            black = np.zeros((1080, 1920, 4), np.uint8)
            return black, black

    def setStingerPremultipliedImages(self, images: list):
        """
        Set the pre-multiplied images of the stinger.

        Args:
            images (list): List of pre-multiplied images.
        """
        self._input_object.setStingerPremultipliedImages(images)

    def getStingerPremultipliedImages(self):
        """
        Get the pre-multiplied images of the stinger.

        Returns:
            list: List of pre-multiplied images.
        """
        return self._input_object.stingerPreMultipliedImages

    def setStingerInvAlphaImages(self, images: list):
        """
        Set the inverse alpha images of the stinger.

        Args:
            images (list): List of inverse alpha images.
        """
        self._input_object.setStingerInvAlphaImages(images)

    def getStingerInvAlphaImages(self):
        """
        Get the inverse alpha images of the stinger.

        Returns:
            list: List of inverse alpha images.
        """
        return self._input_object.stingerInvAlphaImages

    def setCacheData(self, cacheData):
        """
        cache_data = {
            'isCached': True,
            'stingerFolder': self.lneImagePath.text(),
            'premultiplyDirectory': premultiply_directory,
            'invAlphaDirectory': inv_alpha_directory
        }
        :param cacheData:
        :return:
        """
        self._input_object.isCached = cacheData.get('isCached', False)
        self._input_object.stingerInvAlphaImagesPath = cacheData.get('invAlphaDirectory', "")
        self._input_object.stingerPreMultipliedImagesPath = cacheData.get('premultiplyDirectory', "")
        self._input_object.stingerPath = cacheData.get('stingerFolder', "")

    def getLength(self):
        if self._input_object:
            return self._input_object.getLength()
        print("WARNING FROM STINGER DEVICE: Input object not found.")
        return 0

    def setIndex(self, index):
        if self._input_object:
            self._input_object.setIndex(index)

    def onParamsChanged(self, data):
        pass

    def serialize(self):
        """
        Serializes the current state of the input device (Noise generator) into a dictionary.
        """
        data = super().serialize()  # Call the base class method
        data.update({
            "name": self._name,
            "type": "stingerAnimationCapture",
            "params": self.currentParams
        })

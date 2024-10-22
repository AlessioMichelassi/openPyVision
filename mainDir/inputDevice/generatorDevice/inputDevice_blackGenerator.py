import logging

from mainDir.inputDevice.baseDevice.inputDevice_Base import InputDevice_BaseClass, error_logger
from mainDir.inputDevice.generatorDevice.inputObject.generator_Black import BlackGenerator


class InputDevice_BlackGenerator(InputDevice_BaseClass):
    """
    An InputDevice is any input of the mixer.
    It put together the thread, the input object and the graphic interface
    and act as interface to the mixer
    """

    @error_logger.log(log_level=logging.DEBUG)
    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self._frame = None
        # set the input type and create the thread
        self.setInputObject(BlackGenerator())
        # set the graphic interface
        self.graphicInterface = None


    @error_logger.log(log_level=logging.DEBUG)
    def serialize(self):
        """
        This serializes the input object in a dictionary
        Pratically get the variables and put them in a dictionary
        :return:
        """
        data = super().serialize()  # Chiama il metodo della classe base
        return data

    @error_logger.log(log_level=logging.DEBUG)
    def deserialize(self, data):
        """
        Deserialize the input object from a dictionary
        Pratically fill the variables with the data from the dictionary
        :param data:
        :return:
        """
        super().deserialize(data)  # Chiama il metodo della classe base
        # Eventuale logica aggiuntiva se è necessario reimpostare parametri specifici
        self._name = data["name"]

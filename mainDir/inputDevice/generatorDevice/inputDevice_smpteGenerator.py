from mainDir.inputDevice.baseDevice.inputDevice_Base import InputDevice_BaseClass
from mainDir.inputDevice.generatorDevice.generatorWidget.generatorWidget_smpte import GeneratorWidget_Smpte
from mainDir.inputDevice.generatorDevice.inputObject.generator_SMPTE import SMPTEBarsGenerator


class InputDevice_SmpteGenerator(InputDevice_BaseClass):
    """
    An InputDevice is any input of the mixer.
    It put together the thread, the input object and the graphic interface
    and act as interface to the mixer
    """

    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.active = False
        # set the graphic interface
        self.graphicInterface = GeneratorWidget_Smpte(self._input_object)
        # Connect the parametersChanged signal from the widget to handle updates
        self.graphicInterface.paramsChanged.connect(self.onParamsChanged)
        self.currentInputType = "Smpte"
        self.currentParams = {}
        self.updateInputObject(self.currentInputType, self.currentParams)

    def updateInputObject(self, inputType, params):
        print(f"Updating input object to noise type: {inputType} with params: {params}")
        if self._thread and self._thread.isRunning():
            self.stop()
        # Creazione del nuovo inputObject
        inputObject = None
        if inputType == "Smpte":
            inputObject = SMPTEBarsGenerator()
        else:
            print(f"Unknown noise type: {inputType}")
            inputObject = SMPTEBarsGenerator()
        if params:
            inputObject.setParams(params)
        self.setInputObject(inputObject)

    def onTypeChanged(self, data):
        inputType = data.get('type', 'Random')
        print(f"*** Noise Type Changed to {inputType} ***")
        self.currentInputType = inputType
        self.currentParams = {}  # Reset dei parametri
        self.updateInputObject(inputType, self.currentParams)

    def onParamsChanged(self, data):
        # Escludi 'noiseType' dai parametri
        params = data.get('params', {})
        print(f"*** Smpte Parameters Changed: {params} ***")
        self.currentParams.update(params)
        # Aggiorna i parametri dell'inputObject esistente
        self._input_object.setParams(params)

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
        return data

    def deserialize(self, data):
        """
        Deserialize the input object from a dictionary
        Pratically fill the variables with the data from the dictionary
        :param data:
        :return:
        """
        super().deserialize(data)
        self._name = data["name"]

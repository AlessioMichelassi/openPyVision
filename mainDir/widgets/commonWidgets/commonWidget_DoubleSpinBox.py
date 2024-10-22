import logging

from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

from mainDir.errorClass.loggerClass import error_logger


class CustomDoubleSpinBox(QDoubleSpinBox):

    @error_logger.log(log_level=logging.DEBUG)
    def __init__(self, decimalPrecision=2, parent=None):
        super().__init__(parent)
        # Numero di decimali che vuoi visualizzare
        self.setDecimals(decimalPrecision)



    @error_logger.log(log_level=logging.DEBUG)
    def keyPressEvent(self, event):
        """
        Metodo per gestire gli eventi di pressione dei tasti per incrementare
        o decrementare il valore del QDoubleSpinBox.
        Nel caso in cui si abbia un numero decimale: 0.02
        si possono usare le frecce su e giù per incrementare o decrementare il valore
        a sinistra del cursore. 0.0|2 -> 0.03 o 0.01... 0.|02 -> 0.12 o 0.02...
        :param event:
        :return:
        """
        if event.key() in [Qt.Key.Key_Up, Qt.Key.Key_Down]:
            # Ottieni la posizione del caret all'interno del QLineEdit
            lineEdit = self.lineEdit()
            cursor_pos = lineEdit.cursorPosition()
            text = lineEdit.text()

            # Ottieni la posizione del punto decimale nel numero
            decimal_pos = text.find('.')

            if decimal_pos == -1:
                decimal_pos = len(text)  # Se non c'è punto decimale, posizionalo alla fine

            # Determina quale parte del numero aumentare in base alla posizione del cursore
            if cursor_pos > decimal_pos:
                # Se il cursore è dopo il punto decimale
                place_value = 10 ** -(cursor_pos - decimal_pos)
            else:
                # Se il cursore è prima o sul punto decimale
                place_value = 10 ** (decimal_pos - cursor_pos - 1)

            # Determina se incrementare o decrementare
            if event.key() == Qt.Key.Key_Up:
                new_value = self.value() + place_value
            else:
                new_value = self.value() - place_value

            # Imposta il nuovo valore
            self.setValue(new_value)
        elif event.key() == Qt.Key.Key_Return:
            self.editingFinished.emit()
        else:
            super().keyPressEvent(event)

    @error_logger.log(log_level=logging.DEBUG)
    def valueFromText(self, text):
        """
        Forza l'uso del punto come separatore decimale durante l'inserimento del testo
        In Italia si usa la virgola come separatore decimale, poiché
        nel resto del mondo si usa il punto, è necessario forzare l'uso del punto
        come separatore decimale.
        Se uno scrive 2,3 e poi preme invio, il valore sarà 2.3
        :param text:
        :return:
        """
        # Forza l'uso del punto come separatore decimale durante l'inserimento del testo
        text = text.replace(',', '.')  # Sostituisci la virgola con il punto

        try:
            # Prova a convertire il testo in un float
            return float(text)
        except ValueError:
            # Se c'è un errore di conversione, ritorna il valore corrente
            return self.value()  # Non cambiare il valore se il testo non è valido

    @error_logger.log(log_level=logging.DEBUG)
    def textFromValue(self, value):
        """
        Forza l'uso del punto come separatore decimale
        e mantiene i decimali secondo la precisione impostata.
        """
        text = f"{value:.{self.decimals()}f}"  # Mantieni il numero di decimali
        return text.replace(',', '.')  # Sostituisci la virgola con il punto se presente


class CommonWidget_DoubleSpinBox(QWidget):
    paramsChanged = pyqtSignal(dict)

    @error_logger.log(log_level=logging.DEBUG)
    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.name = name.lower().replace(" ", "_")
        self.lblSpinBox = QLabel(self.name, self)
        self.lneSpinBox = QLineEdit(self)
        self.spnBox = CustomDoubleSpinBox()  # Usa la versione personalizzata di QDoubleSpinBox
        self.initUI()
        self.initConnections()
        self._initGeometry()

    @error_logger.log(log_level=logging.DEBUG)
    def initUI(self):
        mainLayout = QVBoxLayout(self)
        mainLayout.addWidget(self.lblSpinBox)
        spinBox_layout = QHBoxLayout()
        spinBox_layout.addWidget(self.lneSpinBox)
        spinBox_layout.addWidget(self.spnBox)
        mainLayout.addLayout(spinBox_layout)
        self.setLayout(mainLayout)

    @error_logger.log(log_level=logging.DEBUG)
    def initDefault(self, _value, _min, _max):
        self.spnBox.setMinimum(_min)
        self.spnBox.setMaximum(_max)
        self.spnBox.setValue(_value)

    @error_logger.log(log_level=logging.DEBUG)
    def initConnections(self):
        self.lneSpinBox.textChanged.connect(self.onTextChange)
        self.spnBox.valueChanged.connect(self.onValueChange)
        # self.lneSpinBox.returnPressed.connect(self.onReturnPressed)
        self.spnBox.editingFinished.connect(self.onReturnPressed)

    @error_logger.log(log_level=logging.DEBUG)
    def _initGeometry(self):
        self.lneSpinBox.setFixedWidth(80)
        self.spnBox.setFixedWidth(100)

    @error_logger.log(log_level=logging.DEBUG)
    def onTextChange(self, text):
        # Forza l'uso del punto al posto della virgola nel testo dell'input line
        if "," in text:
            text = text.replace(",", ".")

        # Se il valore è valido e ha più di un carattere, aggiorna il QDoubleSpinBox
        try:
            floatVar = float(text)
            if len(text) > 0 and not text.endswith("."):
                self.spnBox.setValue(floatVar)
        except ValueError:
            # Se non è valido, ignora l'errore ma non cambia il valore
            pass

    @error_logger.log(log_level=logging.DEBUG)
    def onValueChange(self, value):
        self.lneSpinBox.setText(str(value))

    @error_logger.log(log_level=logging.DEBUG)
    def setParams(self, params, name=None):
        if name is not None:
            self.name = name.lower().replace(" ", "_")
            self.lblSpinBox.setText(name)
        self.lneSpinBox.setText(str(params))
        self.spnBox.setValue(params)

    @error_logger.log(log_level=logging.DEBUG)
    def getParams(self):
        params = {
            self.lblSpinBox.text(): self.spnBox.value()
        }
        return params

    @error_logger.log(log_level=logging.DEBUG)
    def onReturnPressed(self):
        self.paramsChanged.emit(self.getParams())



if __name__ == '__main__':
    test = QApplication([])
    widget = CommonWidget_DoubleSpinBox("Test")
    widget.paramsChanged.connect(print)
    widget.show()
    test.exec()


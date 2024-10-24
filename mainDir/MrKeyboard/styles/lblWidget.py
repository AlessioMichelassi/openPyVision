from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QLineEdit


class LblWidget(QLineEdit):
    lblStyle = """
                QLineEdit {
                    background-color: rgb(20, 20, 25);
                    border: 1px solid rgb(0, 0, 80);
                    border-radius: 5px;
                    color: rgb(153, 204, 255);
                    font-weight: bold;
                    font-size: 12px;
                }
                """

    def __init__(self, name, index, size, parent=None):
        super().__init__(parent)
        if name == "Input":
            self.name = f"Input_{index}"
            self.setText(self.name)
        else:
            self.name = name
            self.setText(self.name)
        self.setBaseSize(QSize(size[0], size[1]))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(self.lblStyle)
        self.setReadOnly(True)
        self.returnPressed.connect(self.onReturnPressed)  # Connect the returnPressed signal to the method

    def mouseDoubleClickEvent(self, event):
        self.setReadOnly(False)

    def focusOutEvent(self, event):
        self.setReadOnly(True)
        self.name = self.text()

    def onReturnPressed(self):
        self.name = self.text()
        self.setReadOnly(True)


# test class

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget

    app = QApplication(sys.argv)
    widget = QWidget()
    layout = QVBoxLayout(widget)
    for i in range(1, 6):
        lbl = LblWidget("Input", i, (100, 30))
        layout.addWidget(lbl)
    widget.show()
    sys.exit(app.exec())

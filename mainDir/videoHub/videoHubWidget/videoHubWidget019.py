from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from mainDir.videoHub.videoHubWidget.videoHub_tabWidget_GenericInput import TabWidget_GenericInput
from mainDir.videoHub.videoHubWidget.videoHub_tabWidget_StillPlayer import TabWidget_StillPlayer
from mainDir.videoHub.videoHubWidget.videoHub_tabWidget_StingerPlayer import TabWidget_StingerPlayer
from mainDir.videoHub.videoHubData018 import VideoHubData018


class VideoHubWidget019(QWidget):
    def __init__(self, _videoHubData, parent=None):
        super().__init__(parent)
        self.videoHubData = _videoHubData
        self.tabWidget = QTabWidget(self)
        self.inputTab1 = TabWidget_GenericInput(self.videoHubData, start=1, end=4)
        self.inputTab2 = TabWidget_GenericInput(self.videoHubData, start=5, end=8)
        self.stillPlayerTab = TabWidget_StillPlayer(self.videoHubData, start=1, end=4)
        self.stingerPlayerTab = TabWidget_StingerPlayer(self.videoHubData, start=1, end=4)
        self.initUI()


    def initUI(self):
        self.tabWidget.addTab(self.inputTab1, "Inputs 1-4")
        self.tabWidget.addTab(self.inputTab2, "Inputs 5-8")
        self.tabWidget.addTab(self.stillPlayerTab, "Still Players")
        self.tabWidget.addTab(self.stingerPlayerTab, "Stinger Players")
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.tabWidget)
        self.setLayout(main_layout)


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication


    app = QApplication(sys.argv)
    videoHubData = VideoHubData018()
    videoHubWidget = VideoHubWidget019(videoHubData)
    videoHubWidget.show()
    sys.exit(app.exec())
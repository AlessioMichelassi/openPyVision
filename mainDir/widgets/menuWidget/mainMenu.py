import json
import logging
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

import numpy as np
import cv2
import sys

from mainDir.widgets.help.helpWidget import HelpWidget

# Configurazione del logger
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("application.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class MenuWidget(QMenuBar):
    _currentName = "untitled"
    MAX_RECENT_FILES = 5

    def __init__(self, mixEffect, main, parent=None):
        super().__init__(parent)
        self.mainWindow = main
        self.parent = parent
        self.mixEffect = mixEffect
        self.settings = QSettings("MyCompany", "OpenPyVisionMixer")  # Inizializza QSettings
        self.recent_files = self.settings.value("recentFiles",
                                                [])  # Carica file recenti o inizializza a una lista vuota

        self.initUI()

    def initUI(self):
        file_menu = self.returnMenuFile()
        edit_menu = self.returnMenuEdit()
        view_menu = self.returnMenuView()
        help_menu = self.returnMenuHelp()

        self.addMenu(file_menu)
        self.addMenu(edit_menu)
        self.addMenu(view_menu)
        self.addMenu(help_menu)

    def returnMenuFile(self):
        file_menu = self.addMenu("File")

        new_action = QAction("New", self)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        # Menu Open Recent
        self.recent_menu = file_menu.addMenu("Open Recent")
        self.update_recent_files_menu()

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save As", self)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.exit_app)
        file_menu.addAction(exit_action)
        return file_menu

    def update_recent_files_menu(self):
        """Aggiorna il menu 'Open Recent' con i file recenti"""
        self.recent_menu.clear()
        for file_name in self.recent_files:
            action = QAction(file_name, self)
            action.triggered.connect(lambda checked, name=file_name: self.open_recent_file(name))
            self.recent_menu.addAction(action)

    def open_recent_file(self, file_name):
        """Apre un file recente"""
        if file_name:
            logger.info(f"Opening recent file: {file_name}")
            print(f"Opening recent file: {file_name}")
            self._currentName = file_name
            self.mixEffect.deserialize(json.load(open(file_name)))
            self.add_to_recent_files(file_name)

    def add_to_recent_files(self, file_name):
        """Aggiunge un file all'elenco dei file recenti"""
        if file_name not in self.recent_files:
            self.recent_files.insert(0, file_name)
            if len(self.recent_files) > self.MAX_RECENT_FILES:
                self.recent_files.pop(-1)
            self.settings.setValue("recentFiles", self.recent_files)
            self.update_recent_files_menu()

    def returnMenuEdit(self):
        edit_menu = self.addMenu("Edit")
        return edit_menu

    def returnMenuView(self):
        # Crea il menu View (Placeholder)
        view_menu = self.addMenu("View")
        setMAinOutFullAction = QAction("Set MainOut Full", self)
        view_menu.addAction(setMAinOutFullAction)

        setMAinOutFullAction.triggered.connect(self.mainWindow.setMainOutFullscreen)
        return view_menu

    def returnMenuHelp(self):
        # Crea il menu Help
        help_menu = self.addMenu("Help")

        about_opvm_action = QAction("About OpVM", self)
        about_opvm_action.triggered.connect(self.about_opvm)
        help_menu.addAction(about_opvm_action)

        about_qt_action = QAction("About Qt", self)
        about_qt_action.triggered.connect(self.about_qt)
        help_menu.addAction(about_qt_action)

        about_numpy_action = QAction("About Numpy", self)
        about_numpy_action.triggered.connect(self.about_numpy)
        help_menu.addAction(about_numpy_action)

        about_opencv_action = QAction("About OpenCV", self)
        about_opencv_action.triggered.connect(self.about_opencv)
        help_menu.addAction(about_opencv_action)

        help_action = QAction("Help", self)
        help_action.triggered.connect(self.help)
        help_menu.addAction(help_action)
        return help_menu

    # Definisci i metodi per le azioni di menu
    def new_file(self):
        logger.info("Creating new file.")
        self._currentName = "untitled"
        self.mainWindow.new_SIGNAL.emit()

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*)")
        if file_name:
            logger.info(f"Opening file: {file_name}")
            print(f"Opening file: {file_name}")
            self._currentName = file_name
            logger.info("File opened successfully.")
            self.add_to_recent_files(file_name)
            self.mainWindow.newAndLoad_SINGAL.emit(json.load(open(file_name)))

    def save_file(self):
        try:
            logger.info(f"Saving file: {self._currentName}.json")
            with open(f"{self._currentName}.json", "w") as f:
                text = json.dumps(self.mixEffect.serialize(), indent=4)
                f.write(text)
                logger.info("File saved successfully.")
                self.add_to_recent_files(f"{self._currentName}.json")
        except Exception as e:
            logger.error(f"Failed to save file: {e}")

    def save_file_as(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File As", "", "All Files (*)")
        if file_name:
            logger.info(f"Saving file as: {file_name}")
            self._currentName = file_name
            self.save_file()

    def exit_app(self):
        logger.info("Exiting application.")
        print("Exit App")
        sys.exit()

    def about_opvm(self):
        logger.info("Displaying About OpVM message.")
        QMessageBox.information(self, "About OpVM", "OpenPyVisionMixer is a video mixing application.")

    def about_qt(self):
        logger.info("Displaying About Qt message.")
        QMessageBox.aboutQt(self)

    def about_numpy(self):
        logger.info("Displaying About Numpy message.")
        QMessageBox.information(self, "About Numpy", f"NumPy version: {np.__version__}")

    def about_opencv(self):
        logger.info("Displaying About OpenCV message.")
        QMessageBox.information(self, "About OpenCV", f"OpenCV version: {cv2.__version__}")

    def help(self):
        logger.info("Displaying Help message.")
        helpWidget = HelpWidget(r"C:\pythonCode\project\openPyVision\openPyVisionBook\openPyVision\mainDir\widgets\help\chapters")
        helpWidget.show()

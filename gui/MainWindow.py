import sys
import traceback

from PyQt5 import uic
import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont

import Settings
from gui import GoogleMapsDialog, SettingsDialog, ConversionProcess

# Following lines make the PyQt framework display error traceback in the console upon program crash
if QtCore.QT_VERSION >= 0x50501:
    def excepthook(type_, value, traceback_):
        traceback.print_exception(type_, value, traceback_)
        QtCore.qFatal('')
sys.excepthook = excepthook

# Load GUI layouts from external files
layout = uic.loadUiType('gui/gui-main_window.ui')[0]
layout_error = uic.loadUiType('gui/gui-error.ui')[0]


class MainWindow(QMainWindow, layout):
    """
    Class defining layout and functions of the main window of the program.
    """
    def __init__(self, parent=None):
        QApplication.setApplicationName('')
        QMainWindow.__init__(self, parent)
        self.setFont(QFont(Settings.font_style, Settings.font_size))
        self.setupUi(self)

        Settings.load_settings()  # Load settings from the serialization file

        # Create instances of sub-windows and underlying processes
        self.settingsDialog = SettingsDialog.SettingsDialog()
        self.error = ErrorAlert()
        self.googleMapsDialog = GoogleMapsDialog.GoogleMapsDialog()
        self.process = ConversionProcess.ConversionProcess()
        self.statusUpdater = ConversionProcess.StatusUpdater()

        # Create connections between sub-windows / underlying processes and main window
        self.statusUpdater.process_stage.connect(self.statusLabel.setText)
        self.statusUpdater.process_percent.connect(self.progressBar.setValue)
        self.googleMapsDialog.update_location.connect(self.update_input_fields)

        self.set_progressBar_value(0)  # Set default value of progress bar

        self.update_input_fields()
        self.show()

    def browse_file_clicked(self):
        # Open dialog window allowing user choose output file
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Choose file location...", "", "", "All files(*)",
                                                   options=options)
        if file_name:
            self.outputField.setText(file_name)

    def settings_tab_clicked(self):
        # Open Settings window
        self.settingsDialog.exec_()

    def set_progressBar_value(self, value):
        self.progressBar.setValue(value)

    def update_input_fields(self):
        """
        Function that updates values in the input fields to values saved in settings.
        """
        Settings.load_settings()
        self.lonField.setText(str(Settings.lon))
        self.latField.setText(str(Settings.lat))
        self.yearField.setText(str(Settings.year))

        self.cityField.setText(Settings.cityname)
        self.regionField.setText(Settings.regionname)
        self.elevationField.setText(str(Settings.elevation))
        self.countryField.setText(Settings.country)

        self.outputField.setText(Settings.output_path)

    def startConversionButton_clicked(self):

        Settings.output_path = self.outputField.text()

        year = self.yearField.text()
        lon = self.lonField.text()
        lat = self.latField.text()

        # Check if input values given by the user are valid
        wrong_data = self.check_input_data(year, lon, lat)

        if wrong_data:
            self.showError()
        else:
            Settings.year = int(year)
            Settings.lon = float(lon)
            Settings.lat = float(lat)
            self.statusUpdater.start()  # Turn on the status updater
            self.process.start()  # Start the conversion process

    def check_input_data(self, year, lon, lat):
        # Check if coordinates are numebrs
        try:
            lon = float(lon)
            lat = float(lat)
        except ValueError:
            return True

        # Check if the coordinates make geographical sense
        if abs(lon) > 180.0 or abs(lat) > 90.0:
            return True
        else:
            return False

    def showError(self):
        self.error.exec_()

    def closeEvent(self, *args, **kwargs):
        """
        Define behaviour upon closing the program
        """
        Settings.year = self.yearField.text()
        Settings.lon = self.lonField.text()
        Settings.lat = self.latField.text()
        Settings.elevation = self.elevationField.text()
        Settings.cityname = self.cityField.text()
        Settings.regionname = self.regionField.text()
        Settings.save_settings()

    def googleButton_clicked(self):
        self.googleMapsDialog.exec_() # Open Google Maps dialog


class ErrorAlert(QDialog, layout_error):
    """
    Class defining error window that is shown to the user when input data is wrong.
    """
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

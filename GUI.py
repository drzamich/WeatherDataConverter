from PyQt5.QtWidgets import *
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
from PyQt5 import uic
import sys, traceback
import Settings
import Preparator
import StationSearcher
import DataReader
import DataConverter
import DataOutputer
import Reporter

layout = uic.loadUiType('gui/gui.ui')[0]
dialog = uic.loadUiType('gui/gui-dialog.ui')[0]
error = uic.loadUiType('gui/gui-error.ui')[0]

if QtCore.QT_VERSION >= 0x50501:
    def excepthook(type_, value, traceback_):
        traceback.print_exception(type_, value, traceback_)
        QtCore.qFatal('')
sys.excepthook = excepthook

class MyWindow(QMainWindow, layout):
    def __init__(self,parent=None):
        QMainWindow.__init__(self,parent)
        self.setupUi(self)

        self.dialog = MyDialog()
        self.error = MyError()

        self.proces = ConversionProcess()
        self.statusUpdater = StatusUpdater()

        self.statusUpdater.proces_stage.connect(self.statusLabel.setText)
        self.statusUpdater.proces_percent.connect(self.progressBar.setValue)

        self.set_progressBar_value(0)
        self.outputField.setText(Settings.output_path)
        self.show()

    def browse_file_clicked(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self,"Choose file location...","","","All files(*)",options=options)
        if fileName:
            self.outputField.setText(fileName)

    def settings_tab_clicked(self):
        self.dialog.exec_()

    def set_progressBar_value(self,value):
        self.progressBar.setValue(value)

    def startConversionButton_clicked(self):
        Settings.output_path = self.outputField.text()

        year = self.yearField.text()
        lon = self.lonField.text()
        lat = self.latField.text()

        wrong_data = self.check_input_data(year,lon,lat)

        if wrong_data:
            self.showError()
        else:
            Settings.year = int(year)
            Settings.lon = float(lon)
            Settings.lat = float(lat)
            self.statusUpdater.start()
            self.proces.start()

    def check_input_data(self,year,lon,lat):
        try:
            year = int(year)
            lon = float(lon)
            lat = float(lat)
        except ValueError:
            return True

        if year > Settings.max_year or year < Settings.min_year:
            return True
        elif abs(lon)>180.0 or abs(lat)>90.0:
            return True
        else:
            return False

    def showError(self):
        self.error.exec_()


class MyDialog(QDialog, dialog):
    def __init__(self,parent=None):
        QDialog.__init__(self,parent)
        self.setupUi(self)
        self.offlineDataField.setText(Settings.dirpath_offline)
        self.programDataField.setText(Settings.dirpath_data)
        self.offlineDataFolderPath = Settings.dirpath_offline
        self.programDataFolderPath = Settings.dirpath_data

    def offlineDataFolderBrowse_clicked(self):
        self.offlineDataFolderPath = QFileDialog.getExistingDirectoryUrl(self,caption='Choose folder',
                                                                         options=QFileDialog.ShowDirsOnly).toString()
        self.offlineDataFolderPath = self.offlineDataFolderPath[8:]
        self.offlineDataField.setText(self.offlineDataFolderPath)


    def programDataFieldBrowse_clicked(self):
        self.programDataFolderPath = QFileDialog.getExistingDirectoryUrl(self,caption='Choose folder',
                                                                         options=QFileDialog.ShowDirsOnly).toString()
        self.programDataFolderPath = self.programDataFolderPath[8:]+'/'
        self.programDataField.setText(self.programDataFolderPath)

    def accept(self):
        #Saving the settings
        Settings.dirpath_data = self.programDataFolderPath
        Settings.dirpath_offline = self.offlineDataFolderPath
        #Closing the window
        super().accept()

    def exec_(self):
        #Updating the fileds. Otherwise they show incorrect information (when they have been edited but
        #not saved before
        self.offlineDataField.setText(Settings.dirpath_offline)
        self.programDataField.setText(Settings.dirpath_data)
        super().exec_()

class MyError(QDialog, error):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)


class ConversionProcess(QtCore.QThread):

    def __init__(self,parent=None):
        super().__init__(parent=parent)

    def run(self):
        Preparator.Preparator()

        StationSearcher.StationSearcher()

        DataReader.DataReader()

        DataConverter.DataConverter()

        DataOutputer.DataOutputer()

        Reporter.Reporter()


class StatusUpdater(QtCore.QThread):
    proces_stage = QtCore.pyqtSignal(str)
    proces_percent = QtCore.pyqtSignal(int)

    def __init__(self,parent=None):
        super().__init__(parent=parent)

    def run(self):
        while True:
            self.send_status(Settings.stage_name,Settings.stage_percent)
            if Settings.stage_name == 'Proces completed':
                break

    def send_status(self, status, percent):
        self.proces_stage.emit(status)
        self.proces_percent.emit(percent)


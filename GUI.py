from PyQt5.QtWidgets import *
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
from PyQt5 import uic
import sys, traceback, os
import Settings
import Preparator
import StationSearcher
import DataReader
import DataConverter
import DataOutputer
import Reporter
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWidgets import QApplication, QWidget, QStyleFactory, QStyle
from PyQt5.QtCore import QUrl, pyqtSlot, QFileInfo
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QFont

layout = uic.loadUiType('gui/gui.ui')[0]
dialog = uic.loadUiType('gui/gui-dialog.ui')[0]
google_maps_dialog = uic.loadUiType('gui/gui-maps.ui')[0]
error = uic.loadUiType('gui/gui-error.ui')[0]

font_style = 'MS Schell DLG 2'

if QtCore.QT_VERSION >= 0x50501:
    def excepthook(type_, value, traceback_):
        traceback.print_exception(type_, value, traceback_)
        QtCore.qFatal('')
sys.excepthook = excepthook

class MyWindow(QMainWindow, layout):
    def __init__(self,parent=None):
        QApplication.setApplicationName('')
        QMainWindow.__init__(self,parent)
        self.setupUi(self)
        self.setFont(QFont(font_style,8))
        Settings.load_settings()

        self.dialog = MyDialog()
        self.error = MyError()
        self.googleMapsDialog = GoogleMapsDialog()

        self.proces = ConversionProcess()
        self.statusUpdater = StatusUpdater()

        self.statusUpdater.proces_stage.connect(self.statusLabel.setText)
        self.statusUpdater.proces_percent.connect(self.progressBar.setValue)

        self.googleMapsDialog.update_location.connect(self.update_input_fields)

        self.set_progressBar_value(0)

        self.setStyle(QStyleFactory.create("windowsvista"))
        self.update_input_fields()
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

    def update_input_fields(self):
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

    def closeEvent(self, *args, **kwargs):
        Settings.year = self.yearField.text()
        Settings.lon = self.lonField.text()
        Settings.lat = self.latField.text()
        Settings.elevation = self.elevationField.text()
        Settings.cityname = self.cityField.text()
        Settings.regionname = self.regionField.text()
        Settings.save_settings()

    def inputField_edited(self):
        pass

    def googleButton_clicked(self):
        self.googleMapsDialog.exec_()

class MyDialog(QDialog, dialog):
    def __init__(self,parent=None):
        QDialog.__init__(self,parent)
        self.setupUi(self)
        self.setFont(QFont(font_style,8))
        self.output_directory = Settings.output_directory
        self.offline_data_directory = Settings.dirpath_offline

    def setupFields(self):
        self.offlineDataField.setText(Settings.dirpath_offline)
        self.outputPathField.setText(Settings.output_directory)

        self.ftpAdressField.setText(Settings.ftp_adress)
        self.ftpUserField.setText(Settings.ftp_user)
        self.ftpPassField.setText(Settings.ftp_pass)
        self.ftpPathField.setText(Settings.ftp_dirpath)

        self.minRecField.setText(str(Settings.min_rec))

        if Settings.use_offline_data:
            self.offlineData_checkBox.setCheckState(2) #checked
        else:
            self.offlineData_checkBox.setCheckState(0) #unchecked

        if Settings.tabular_reports:
            self.tabular_checkBox.setCheckState(2) #checked
        else:
            self.tabular_checkBox.setCheckState(0) #unchecked

    def offlineDataFolderBrowse_clicked(self):
        self.offline_data_directory = QFileDialog.getExistingDirectoryUrl(self,caption='Choose folder',
                                                                         options=QFileDialog.ShowDirsOnly).toString()
        self.offline_data_directory = self.offline_data_directory[8:]+'/'
        self.offlineDataField.setText(self.offline_data_directory)


    def outputPathFieldBrowse_clicked(self):
        self.output_directory = QFileDialog.getExistingDirectoryUrl(self, caption='Choose folder',
                                                               options=QFileDialog.ShowDirsOnly).toString()
        self.output_directory = self.output_directory[8:] + '/'
        self.outputPathField.setText(self.output_directory)

    def accept(self):
        #Saving the settings
        Settings.output_directory = self.output_directory
        Settings.output_path = self.output_directory+'Output.epw'
        Settings.dirpath_offline = self.offline_data_directory

        Settings.ftp_dirpath = self.ftpPathField.text()
        Settings.ftp_user = self.ftpUserField.text()
        Settings.ftp_adress = self.ftpAdressField.text()
        Settings.ftp_pass = self.ftpPassField.text()

        Settings.min_rec = int(self.minRecField.text())

        offline_data_checked = self.offlineData_checkBox.isChecked()
        tabular_reports_checked = self.tabular_checkBox.isChecked()

        if offline_data_checked:
            Settings.use_offline_data = True
        else:
            Settings.use_offline_data = False

        if tabular_reports_checked:
            Settings.tabular_reports = True
        else:
            Settings.tabular_reports = False

        Settings.save_settings()

        #Closing the window
        super().accept()

    def exec_(self):
        self.setupFields()
        super().exec_()

    def ftpDefaultsButton_clicked(self):
        self.ftpAdressField.setText('ftp-cdc.dwd.de')
        self.ftpUserField.setText('anonymous')
        self.ftpPassField.setText('')
        self.ftpPathField.setText('/pub/CDC/observations_germany/climate/hourly/')

class MyError(QDialog, error):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)


class GoogleMapsDialog(QDialog, google_maps_dialog):
    update_location = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.lat = Settings.lat
        self.lng = Settings.lon
        self.city = Settings.cityname
        self.region = Settings.regionname
        self.country = Settings.country
        self.elevation = Settings.elevation
        self.setupUi(self)
        self.setFont(QFont(font_style,8))
        self.mapsWidget = QWidget(self)
        self.webView = QWebEngineView(self.mapsWidget)
        channel = QWebChannel(self.webView.page())
        self.webView.page().setWebChannel(channel)
        channel.registerObject('backend',self)

        self.mapsWidget.setFixedSize(350,350)

        htmlMapFile = QUrl.fromLocalFile(QFileInfo('map.html').absoluteFilePath())
        self.webView.page().load(htmlMapFile)

    def accept(self):
        Settings.lat = self.lat
        Settings.lon = self.lng
        Settings.cityname = self.city
        Settings.regionname = self.region
        Settings.country = self.country
        Settings.elevation = self.elevation
        Settings.save_settings()

        self.update_location.emit()

        super().accept()

    @pyqtSlot(float, float, str, str, str,float)
    def getpos(self, lat=51.05, lng=13.74, city='Dresden', region='Saxony', country='DE',elevation = 113.0):
        self.lat = format(lat, '.2f')
        self.lng = format(lng, '.2f')
        self.city = city.lstrip()  #removing preceding whitespaces
        self.region = region
        self.country = country
        self.elevation = format(elevation,'.2f')

class ConversionProcess(QtCore.QThread):

    def __init__(self,parent=None):
        super().__init__(parent=parent)

    def run(self):
        # Preparator.Preparator()

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


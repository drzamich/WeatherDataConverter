from PyQt5.QtWidgets import *
from PyQt5 import uic
import Settings
from PyQt5.QtGui import QFont
from gui.MainWindow import font_style

layout = uic.loadUiType('gui/gui-settings.ui')[0]

class SettingsDialog(QDialog, layout):
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
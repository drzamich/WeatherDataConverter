import os
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QFont

import Settings

layout = uic.loadUiType('gui/gui-settings.ui')[0]  # Load layout from the external file


class SettingsDialog(QDialog, layout):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setFont(QFont(Settings.font_style, Settings.font_size))
        self.output_directory = Settings.output_directory
        self.offline_data_directory = Settings.dirpath_offline

    def setup_fields(self):
        # Filling fields in the dialog window with values saved in the Settings.
        self.offlineDataField.setText(Settings.dirpath_offline)
        self.outputPathField.setText(Settings.output_directory)

        self.ftpAdressField.setText(Settings.ftp_adress)
        self.ftpUserField.setText(Settings.ftp_user)
        self.ftpPassField.setText(Settings.ftp_pass)
        self.ftpPathField.setText(Settings.ftp_dirpath)

        self.minRecField.setText(str(Settings.min_rec))

        if Settings.use_offline_data:
            self.offlineData_checkBox.setCheckState(2)  # checked
        else:
            self.offlineData_checkBox.setCheckState(0)  # unchecked

        if Settings.interpolate_data:
            self.interpolate_data_checkBox.setCheckState(2)  # checked
        else:
            self.interpolate_data_checkBox.setCheckState(0)  # unchecked

        if Settings.tabular_reports:
            self.tabular_checkBox.setCheckState(2)  # checked
        else:
            self.tabular_checkBox.setCheckState(0)  # unchecked

    def offlineDataFolderBrowse_clicked(self):
        # Opens dialog window allowing user to choose location of the offline weather data
        self.offline_data_directory = QFileDialog.getExistingDirectoryUrl(self, caption='Choose folder',
                                                                          options=QFileDialog.ShowDirsOnly).toString()
        self.offline_data_directory = self.offline_data_directory[8:] #+ os.sep
        self.offlineDataField.setText(self.offline_data_directory)

    def outputPathFieldBrowse_clicked(self):
        # Opens dialog window allowing user to choose the default output directory
        self.output_directory = QFileDialog.getExistingDirectoryUrl(self, caption='Choose folder',
                                                                    options=QFileDialog.ShowDirsOnly).toString()
        self.output_directory = self.output_directory[8:] #+ os.sep
        self.outputPathField.setText(self.output_directory)

    def accept(self):
        """
        Defining behaviour when user clicks on 'OK' button.
        """
        # Saving the settings
        Settings.output_directory = self.output_directory
        Settings.output_path = self.output_directory + '/Output.epw'
        Settings.dirpath_offline = self.offline_data_directory

        Settings.ftp_dirpath = self.ftpPathField.text()
        Settings.ftp_user = self.ftpUserField.text()
        Settings.ftp_adress = self.ftpAdressField.text()
        Settings.ftp_pass = self.ftpPassField.text()

        Settings.min_rec = int(self.minRecField.text())

        offline_data_checked = self.offlineData_checkBox.isChecked()
        tabular_reports_checked = self.tabular_checkBox.isChecked()
        interpolate_data_checked = self.interpolate_data_checkBox.isChecked()

        if offline_data_checked:
            Settings.use_offline_data = True
        else:
            Settings.use_offline_data = False

        if tabular_reports_checked:
            Settings.tabular_reports = True
        else:
            Settings.tabular_reports = False

        if interpolate_data_checked:
            Settings.interpolate_data = True
        else:
            Settings.interpolate_data = False

        Settings.save_settings()

        # Closing the window
        super().accept()

    def exec_(self):
        self.setup_fields()
        super().exec_()

    def ftpDefaultsButton_clicked(self):
        # Resetting input fields on the 'FTP' tab to the default values.
        self.ftpAdressField.setText('ftp-cdc.dwd.de')
        self.ftpUserField.setText('anonymous')
        self.ftpPassField.setText('')
        self.ftpPathField.setText('/pub/CDC/observations_germany/climate/hourly/')

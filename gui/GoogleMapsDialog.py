from PyQt5.QtWidgets import *
import PyQt5.QtCore as QtCore
from PyQt5 import uic
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QUrl, pyqtSlot, QFileInfo
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QFont

import Settings

layout = uic.loadUiType('gui/gui-maps.ui')[0]  # Load layout from the external file


class GoogleMapsDialog(QDialog, layout):
    update_location = QtCore.pyqtSignal()  # Signal that is sent to the main window to update the input fields

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setFont(QFont(Settings.font_style, Settings.font_size))

        self.lat = Settings.lat
        self.lng = Settings.lon
        self.city = Settings.cityname
        self.region = Settings.regionname
        self.country = Settings.country
        self.elevation = Settings.elevation

        # Create a map Widget
        self.mapsWidget = QWidget(self)
        self.webView = QWebEngineView(self.mapsWidget)

        # Create a channel between python and website
        channel = QWebChannel(self.webView.page())
        self.webView.page().setWebChannel(channel)
        channel.registerObject('backend', self)  # Register the Python class as 'backend' in JavaScript

        self.mapsWidget.setFixedSize(350, 350)

        html_map_file = QUrl.fromLocalFile(QFileInfo('gui/map.html').absoluteFilePath())
        self.webView.page().load(html_map_file)

    def accept(self):
        # Define behaviour when clicking the 'OK' button
        Settings.lat = self.lat
        Settings.lon = self.lng
        Settings.cityname = self.city
        Settings.regionname = self.region
        Settings.country = self.country
        Settings.elevation = self.elevation

        Settings.save_settings()

        self.update_location.emit()  # Send signal to the MainWindow triggering update of the input fields

        super().accept()

    # Defining slot that is responsible for receiving signals from the JavaScript
    @pyqtSlot(float, float, str, str, str, float)
    def getpos(self, lat=51.05, lng=13.74, city='Dresden', region='Saxony', country='DE', elevation=113.0):
        """
        Function responsible for getting data from the JavaScript and saving it as class attributes
        """
        self.lat = format(lat, '.2f')
        self.lng = format(lng, '.2f')
        self.city = city.lstrip()  # removing preceding whitespaces
        self.region = region
        self.country = country
        self.elevation = format(elevation, '.2f')

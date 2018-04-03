from PyQt5.QtWidgets import *
import PyQt5.QtCore as QtCore
from PyQt5 import uic
import Settings
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QUrl, pyqtSlot, QFileInfo
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QFont

layout = uic.loadUiType('gui/gui-maps.ui')[0]


class GoogleMapsDialog(QDialog, layout):
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
        self.setFont(QFont(Settings.font_style,8))
        self.mapsWidget = QWidget(self)
        self.webView = QWebEngineView(self.mapsWidget)
        channel = QWebChannel(self.webView.page())
        self.webView.page().setWebChannel(channel)
        channel.registerObject('backend',self)

        self.mapsWidget.setFixedSize(350,350)

        htmlMapFile = QUrl.fromLocalFile(QFileInfo('gui/map.html').absoluteFilePath())
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
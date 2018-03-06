from PyQt5.QtWidgets import *
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
import Settings
import StationSearcher
import DataReader
import DataConverter
import DataOutputer
import Reporter

class GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.proces = proces()
        self.statusUpdater = statusUpdater()
        self.initUI()


    def initUI(self):
        l0 = QLabel(self)
        l0.setText('Weather data converter')
        l0.setAlignment(QtCore.Qt.AlignCenter)

        self.f1 = QLineEdit()
        self.f2 = QLineEdit()
        self.f3 = QLineEdit()

        form = QFormLayout()
        form.addRow(QLabel('Longitude [deg]'),self.f1)
        form.addRow(QLabel('Latitude [deg]'),self.f2)
        form.addRow(QLabel('Year'),self.f3)

        btn = QPushButton('Run converstion',self)
        btn.clicked.connect(lambda: self.btn_clk())
        btn.resize(btn.sizeHint())

        self.statusBar = QLabel(self)
        self.statusBar.setText(Settings.stage_name)

        self.progress = QProgressBar(self)
        self.progress.setGeometry(200,80,250,20)

        vbox = QVBoxLayout()
        vbox.addWidget(l0)
        vbox.addLayout(form)
        vbox.addWidget(btn)
        vbox.addWidget(self.statusBar)
        vbox.addWidget(self.progress)

        self.statusUpdater.proces_stage.connect(self.statusBar.setText)
        self.statusUpdater.proces_percent.connect(self.progress.setValue)

        self.setGeometry(300,300,300,220)
        self.setWindowTitle('Weather Data Converter')
        self.setWindowIcon(QtGui.QIcon('pythonlogo.png'))
        self.setLayout(vbox)
        self.show()

    def btn_clk(self):
        Settings.lon = float(self.f1.text())
        Settings.lat = float(self.f2.text())
        Settings.year = int(self.f3.text())
        self.statusUpdater.start()
        self.proces.start()


class proces(QtCore.QThread):

    def __init__(self,parent=None):
        super().__init__(parent=parent)

    def run(self):
        StationSearcher.StationSearcher()

        DataReader.DataReader()

        DataConverter.DataConverter()

        DataOutputer.DataOutputer()

        Reporter.Reporter()


class statusUpdater(QtCore.QThread):
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


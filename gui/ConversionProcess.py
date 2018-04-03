import PyQt5.QtCore as QtCore

import StationSearcher
import DataReader
import DataConverter
import DataOutputer
import Reporter


class ConversionProcess(QtCore.QThread):

    def __init__(self,parent=None):
        super().__init__(parent=parent)

    def run(self):

        StationSearcher.StationSearcher()

        if Reporter.complete_station_list:
            DataReader.DataReader()

            DataConverter.DataConverter()

            DataOutputer.DataOutputer()

            Reporter.Reporter()

        else:
            # Setting control variable back to default in order to allow the re-run
            Reporter.complete_station_list = True


class StatusUpdater(QtCore.QThread):
    proces_stage = QtCore.pyqtSignal(str)
    proces_percent = QtCore.pyqtSignal(int)

    def __init__(self,parent=None):
        super().__init__(parent=parent)

    def run(self):
        while True:
            self.send_status(Reporter.stage_name,Reporter.stage_percent)
            if Reporter.stage_name == 'Proces completed':
                break

    def send_status(self, status, percent):
        self.proces_stage.emit(status)
        self.proces_percent.emit(percent)
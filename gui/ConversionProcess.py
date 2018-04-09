import PyQt5.QtCore as QtCore

import StationSearcher
import DataReader
import DataConverter
import DataOutputer
import Reporter


class ConversionProcess(QtCore.QThread):
    """
    Class defining the thread process for the weather data extraction and conversion.
    Input parameters for the process are defined in the MainWindow and saved in Settings module.
    """
    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def run(self):
        Reporter.set_status('Start of the process',1)
        # Create list of 7 stations that are most favorable to extract weather data from for
        # the given input parameters
        StationSearcher.StationSearcher()

        # Process proceeds only when it was successful to create a complete set of stations used later
        # for data extraction
        if Reporter.complete_station_list:
            # Based on the list of stations, download and extract the weather data from zip files
            DataReader.DataReader()

            # Interpolate values for missing data, calculate additional values based on the weather data
            DataConverter.DataConverter()

            # Prepare and save the .epw file based on the converted weather data
            DataOutputer.DataOutputer()

            # Prepare and save reports containing information about stations, missing values
            # as well as files containing weather data values in a easy-to-evaluate form
            Reporter.Reporter()
            Reporter.set_status('Process completed', 100)

        # When the station list is incomplete, the conversion process stops
        else:
            # Setting control variable back to default in order to allow the re-run
            Reporter.complete_station_list = True


class StatusUpdater(QtCore.QThread):
    """
    Class defining thread that is responsible for sending the information about current stage of the
    conversion process to the main window
    """
    process_stage = QtCore.pyqtSignal(str)  # Signal containing
    process_percent = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def run(self):
        while True:
            self.send_status(Reporter.stage_name, Reporter.stage_percent)
            # if Reporter.stage_name == 'Process completed':
            #     self.send_status(Reporter.stage_name, Reporter.stage_percent)
            #     break

    def send_status(self, status, percent):
        # Send signals with current stage to the main window
        self.process_stage.emit(status)
        self.process_percent.emit(percent)

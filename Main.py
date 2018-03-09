import Preparator
import StationSearcher
import DataReader
import DataConverter
import DataOutputer
import Reporter
import GUI
import sys
from PyQt5.QtWidgets import QApplication


if __name__ == '__main__':


    #Calling the GUI
    app = QApplication(sys.argv)
    gui = GUI.MyWindow()
    sys.exit(app.exec_())

    #Preparing folders
    Preparator.Preparator()

    # Calling the StationSearcher constructor using input parameters
    # Output -  list of 7 stations that are most favourable for given input paramaters, saved in variable station_list
    StationSearcher.StationSearcher()

    # Calling the DataReader constructor using previously created station list
    # Output - unconverted set of data extracted from zip files in the form of list
    DataReader.DataReader()

    #Calling the DataConverter constructor using previously created raw data
    #Output: converted data with calculated additional values needed in energy analisys programs
    #Additionally, periods with missing entries in the original data set as well as number of those enries are saved
    DataConverter.DataConverter()

    # print(Reporter.station_list)
    #Writing the EPW file
    DataOutputer.DataOutputer()

    #Calling the Reporter class that based on the data generated in steps before, creates report files in the reports/
    #directory
    Reporter.Reporter()



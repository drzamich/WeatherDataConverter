import datetime
import os
from prettytable import PrettyTable

import Settings

# Variables storing data created by other modules
station_list = []
extracted_data = []
converted_data = []
missing_list = []
missing_entries_list = []


class Reporter:
    """
    Class responsible for generating report txt files that allow user to check the correctness of extracted
    weather data.
    """
    def __init__(self):
        print('Reporter')
        set_status('Preparing reports', 90)

        self.year = Settings.year
        self.lon = Settings.lon
        self.lat = Settings.lat

        self.station_list = station_list
        self.missing_dates = missing_list
        self.missing_entries = missing_entries_list
        self.extracted_data = extracted_data
        self.converted_data = converted_data

        # Create subfolder in the reports/ directory
        self.create_folders()

        # Generate report txt file with staions list and number of missing values per climate element
        set_status('Preparing reports... saving report file', 91)
        self.generate_report()

        # Generate files with missing periods per climate element
        set_status('Preparing reports... saving missing values file', 92)
        self.save_missing_values()

        # Generate txt files with raw data extracted from stations
        if Settings.tabular_reports:
            self.save_extracted_data_table()
        else:
            self.save_extracted_data()

        # Generate txt files with interpolated and recalculated data
        if Settings.tabular_reports:
            self.save_converted_data_table()
        else:
            self.save_converted_data()

        set_status('Process completed', 100)

    def create_folders(self):
        """
        Function creates necessary subfolders in the reports/ directory
        """
        current_date_ts = datetime.datetime.now()
        current_date = current_date_ts.strftime('%Y%m%d - %H%M%S')
        self.dirpath = Settings.dirpath_program + os.sep + 'reports' + os.sep + current_date + os.sep

        os.mkdir(self.dirpath)
        os.mkdir(self.dirpath + 'converted_data')
        os.mkdir(self.dirpath + 'raw_data')

    def generate_report(self):
        """
        Function generates report txt file with stations list and number of missing values per climate element
        """
        # Using the imported PrettyTable class, creating a table to present the list of stations choosen for the
        # data extraction
        table = PrettyTable(
            ['Char', 'Short', 'ID', 'DateStart', 'DateEnd', 'Elev.', 'Lat.', 'Lon.', 'City', 'Bundesland'])
        for station in self.station_list:
            table.add_row(station)

        # Creating report text to be written at the beginning of the report file
        report_text = ('Data extraction executed at %s \n' % str(datetime.datetime.now())
                       + 'Chosen year: %s \n' % str(self.year)
                       + 'Latitude: %s \n' % str(self.lat)
                       + 'Longitude: %s \n\n' % str(self.lon)
                       + 'List of most favourable weather stations: \n')

        # Saving the report text and table with stations in the file 00_report.txt
        f = open(self.dirpath + '00_report.txt', 'a')
        f.write(report_text)
        f.write(str(table))

        # Writing in the report file number of missing entries in the original data set for each climate  element
        for index, station in enumerate(self.station_list):
            report_text = ('\nSuccessfully extracted data for ' + station[0] + '\n'
                           + 'There are %i missing entries in the original data set \n' % self.missing_entries[
                               index])
            f.write(report_text)
        f.close()

    def save_missing_values(self):
        """
        Function generates files with missing periods per climate element
        """
        # Writing in the 00_missing_values.txt file, all the time periods with missing entries in the original data set
        f = open(self.dirpath + '00_missing_values.txt', 'a')

        for index, list in enumerate(self.missing_dates):
            f.write(Settings.observedCharacteristics[index][0] + '\n')
            if index == 6: # exception for sunshine duration data
                f.write('Missing values between 21:00 and 2:00 were omitted')
            for item in list:
                f.write(str(item) + '\n')
            f.write('\n')
        f.close()

    def save_extracted_data(self):
        """
        Function txt files with raw data extracted from stations in the raw form (pure Python list).
        """
        for index, station in enumerate(self.station_list):
            char_name = station[0]

            percent = index + 1
            set_status('Preparing reports... raw data for ' + char_name, 92 + percent)

            filepath = self.dirpath + 'raw_data' + os.sep + char_name + '.txt'
            f = open(filepath, 'a')
            for entry in self.extracted_data[index]:
                f.write(str(entry) + '\n')
            f.close()

    def save_extracted_data_table(self):
        """
        Function txt files with raw data extracted from stations in the form of table with headers.
        """
        for index, station in enumerate(self.station_list):
            char_name = station[0]

            percent = index + 1
            set_status('Preparing reports... raw data for ' + char_name, 92 + percent / 2)

            table = PrettyTable(headers_raw_data[index])

            for entry in self.extracted_data[index]:
                table.add_row(entry)

            filepath = self.dirpath + os.sep + 'raw_data' + os.sep + char_name + '.txt'
            f = open(filepath, 'a')
            f.write(str(table))
            f.close()

    def save_converted_data(self):
        """
        Function creates txt files with interpolated and recalculated data in the raw form (pure Python list).
        """
        for index, station in enumerate(self.station_list):
            char_name = station[0]

            percent = index + 1
            set_status('Preparing reports... converted data for ' + char_name, 95.5 + percent / 2)

            filepath = self.dirpath + 'converted_data' + os.sep + char_name + '.txt'
            f = open(filepath, 'a')
            for entry in self.converted_data[index]:
                f.write(str(entry) + '\n')
            f.close()

    def save_converted_data_table(self):
        """
        Function creates txt files with interpolated and recalculated data in the form of table with headers.
        """
        for index, station in enumerate(self.station_list):
            char_name = station[0]

            percent = index + 1
            set_status('Preparing reports... converted data for ' + char_name, 95.5 + percent / 2)

            table = PrettyTable(headers_converted_data[index])
            for entry in self.converted_data[index]:
                table.add_row(entry)

            filepath = self.dirpath + 'converted_data' + os.sep + char_name + '.txt'
            f = open(filepath, 'a')
            f.write(str(table))
            f.close()

"""
Variables storing information about current stage of the conversion process
"""
stage_name = ''
stage_percent = 0


def set_status(stage_name_new, stage_percent_new):
    """
    Function changing values of the variables storing information about current stage of the conversion process
    """
    global stage_name, stage_percent
    stage_name = stage_name_new
    stage_percent = stage_percent_new


"""
Variables storing headers for tables with data saved in reports
"""
headers_raw_data = [
    ['Date', 'Air Temp. [*C]', 'Rel. humid. [%]'],
    ['Date', 'Total cloud cover [1/8]'],
    ['Date', 'Hrly precipitation height [mm]'],
    ['Date', 'Mean sea level pressure [hPa]', 'Pressure at station height [hPa]'],
    ['Date', 'T at depth [*C]: 2 cm', '5 cm', '10 cm', '20 cm', '50 cm', '100 cm'],
    ['Date', 'Hrly longwave dwnwrd rad. [J/cm2]', 'Hrly diff solar rad. [J/cm2]', 'Hrly solar incoming rad. [J/cm2]',
     'Sunshine duration [min]', 'Zenith angle [*]'],
    ['Date', 'Sunshine duration [min]'],
    ['Date', 'Wind speed [m/s]', 'Wind direction [Grad]']
]

headers_converted_data = [
    ['Date', '(r)Air Temp. [*C]', '(r)Rel. humid. [%]', 'Dry Bulb Temp. [*C]', 'Dew Point Temp [*C]',
     'Rel. Humid. [%]'],
    ['Date', '(r)Total cloud cover [1/8]', 'Total Sky Cover [1/10]'],
    ['Date', '(r)Hrly precipitation height [mm]'],
    ['Date', '(r)Mean sea level pressure [hPa]', '(r)Pressure at station height [hPa]',
     'Atmosphetic Station Pressure [Pa]'],
    ['Date', '(r)T at depth [*C]: 2 cm', '(r)5 cm', '(r)10 cm', '(r)20 cm', '(r)50 cm', '(r)100 cm'],
    ['Date', '(r)Hrly longwave dwnwrd rad. [J/cm2]', '(r)Hrly diff solar rad. [J/cm2]',
     '(r)Hrly solar incoming rad. [J/cm2]',
     '(r)Sunshine duration [min]', '(r)Zenith angle [*]', 'Diff. Horiz. Irrad. [W/m2]', 'Glob. Horiz. Irrad. [W/m2]',
     'Dir. Norm. Irrad. [W/m2]', 'Horiz. Infrared Radiat. Intens. [W/m2]'],
    ['Date', '(r)Sunshine duration [min]'],
    ['Date', '(r)Wind speed [m/s]', '(r)Wind direction [Grad]', 'Wind Direction [*]', 'Wind Speed [m/s]']
]

"""
Flag that stores information whether it was successful or not to create a complete station list 
"""
complete_station_list = True

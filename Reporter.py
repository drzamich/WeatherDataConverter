from prettytable import PrettyTable
import Settings
import os
import datetime


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
        setStatus('Preparing reports', 90)
        self.year = Settings.year
        self.lon = Settings.lon
        self.lat = Settings.lat


        self.station_list = station_list
        self.missing_dates = missing_list
        self.missing_entries = missing_entries_list
        self.extracted_data = extracted_data
        self.converted_data = converted_data

        #Create subfolder in the reports/ directory
        self.create_folder()

        #Generate report txt file with staions list and number of missing values per climate element
        self.generate_report()

        #Generate files with missing periods per climate element
        self.save_missing_values()

        #Generate txt files with raw data extracted from stations
        self.save_extracted_data()

        #Generate txt files with intepolated and recalculated data
        self.save_converted_data()

        setStatus('Process completed', 100)
    def create_folder(self):
        """
        Functon creates necessary subfolders in the reports/ directory
        """
        current_date_ts = datetime.datetime.now()
        current_date = current_date_ts.strftime('%Y%m%d - %H%M%S')
        self.dirpath = Settings.dirpath_data+'reports/' + current_date + '/'
        os.mkdir(self.dirpath)
        os.mkdir(self.dirpath+'converted_data/')
        os.mkdir(self.dirpath + 'raw_data/')

    def generate_report(self):
        """
        Function generates report txt file with staions list and number of missing values per climate element
        """

        #Using the imported PrettyTable class, creating a table to present the list of stations choosen for the
        #data extraction
        table = PrettyTable(['Char', 'Short', 'ID', 'DateStart', 'DateEnd', 'Elev.', 'Lat.', 'Lon.', 'City', 'Bundesland'])
        for station in self.station_list:
            table.add_row(station)

        #Creating report text to be written at the beginning of the report file
        report_text = ('Data extraction executed at %s \n' % str(datetime.datetime.now())
        +'Choosen year: %s \n' %str(self.year)
        +'Latitude: %s \n' %str(self.lat)
        +'Lognitude: %s \n\n'%str(self.lon)
        +'List of most favourable weather stations: \n')

        #Saving the report text and table with stations in the file 00_report.txt
        f = open(self.dirpath+'00_report.txt','a')
        f.write(report_text)
        f.write(str(table))

        #Writing in the report file number of missing entries in the original data set for each climate  element
        for index,station in enumerate(self.station_list):
            report_text = ('\nSuccesfully extracted data for '+station[0]+'\n'
                +'There are %i missing hour entries in the original gdata set \n' % self.missing_entries[index])
            f.write(report_text)
        f.close()

    def save_missing_values(self):
        """
        Function generates files with missing periods per climate element
        """
        #Writing in the 00_missing_values.txt file, all the time periods with missing entries in the original data set
        f = open(self.dirpath + '00_missing_values.txt', 'a')

        for index,list in enumerate(self.missing_dates):
            f.write(Settings.observedCharacteristics[index][0]+'\n')
            for item in list:
                f.write(str(item)+'\n')
            f.write('\n')
        f.close()

    def save_extracted_data(self):
        """
        Function txt files with raw data extracted from stations in the raw form (pure Python list).
        """
        for index, station in enumerate(self.station_list):
            char_name = station[0]

            filepath = self.dirpath + 'raw_data/' + char_name + '.txt'
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

            table = PrettyTable(Settings.headers_raw_data[index])

            for entry in self.extracted_data[index]:
                table.add_row(entry)

            filepath = self.dirpath + '/raw_data/' + char_name + '.txt'
            f = open(filepath, 'a')
            f.write(str(table))
            f.close()

    def save_converted_data(self):
        """
        Function creates txt files with interpolated and recalculated data in the raw form (pure Python list).
        """
        for index, station in enumerate(self.station_list):
            char_name = station[0]

            filepath = self.dirpath + 'converted_data/' + char_name + '.txt'
            f = open(filepath, 'a')
            for entry in self.converted_data[index]:
                f.write(str(entry)+'\n')
            f.close()

    def save_converted_data_table(self):
        """
        Function creates txt files with interpolated and recalculated data in the form of table with headers.
        """
        for index, station in enumerate(self.station_list):
            char_name = station[0]

            table = PrettyTable(Settings.headers_converted_data[index])
            for entry in self.converted_data[index]:
                table.add_row(entry)

            filepath = self.dirpath + 'converted_data/'+char_name+'.txt'
            f = open(filepath,'a')
            f.write(str(table))
            f.close()

def setStatus(stage_name_new, stage_percent_new):
    Settings.stage_name = stage_name_new
    Settings.stage_percent = stage_percent_new


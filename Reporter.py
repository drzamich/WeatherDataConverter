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

    def __init__(self):
        print('Reporter')
        self.year = Settings.year
        self.lon = Settings.lon
        self.lat = Settings.lat


        self.station_list = station_list
        self.missing_dates = missing_list
        self.missing_entries = missing_entries_list
        self.extracted_data = extracted_data
        self.converted_data = converted_data

        self.create_folder()
        self.generate_report()
        self.save_missing_values()
        self.save_converted_data()
        self.save_extracted_data()


    def create_folder(self):
        current_date_ts = datetime.datetime.now()
        current_date = current_date_ts.strftime('%Y%m%d - %H%M%S')
        self.dirpath = 'reports/' + current_date + '/'
        os.mkdir(self.dirpath)
        os.mkdir(self.dirpath+'converted_data/')
        os.mkdir(self.dirpath + 'raw_data/')

    def generate_report(self):
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
                +'There are %i missing hour entries in the original data set \n' % self.missing_entries[index])
            f.write(report_text)
        f.close()

    def save_missing_values(self):
        #Writing in the 00_missing_values.txt file, all the time periods with missing entries in the original data set
        f = open(self.dirpath + '00_missing_values.txt', 'a')

        for index,list in enumerate(self.missing_dates):
            f.write(Settings.observedCharacteristics[index][0]+'\n')
            for item in list:
                f.write(str(item)+'\n')
            f.write('\n')
        f.close()


    def save_converted_data_table(self):
        for index, station in enumerate(self.station_list):
            char_name = station[0]

            table = PrettyTable(Settings.headers_converted_data[index])
            for entry in self.converted_data[index]:
                table.add_row(entry)

            filepath = self.dirpath + 'converted_data/'+char_name+'.txt'
            f = open(filepath,'a')
            f.write(str(table))
            f.close()


    def save_extracted_data_table(self):
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
        for index, station in enumerate(self.station_list):
            char_name = station[0]

            filepath = self.dirpath + 'converted_data/' + char_name + '.txt'
            f = open(filepath, 'a')
            for entry in self.converted_data[index]:
                f.write(str(entry)+'\n')
            f.close()

    def save_extracted_data(self):
        for index, station in enumerate(self.station_list):
            char_name = station[0]

            filepath = self.dirpath + 'raw_data/' + char_name + '.txt'
            f = open(filepath, 'a')
            for entry in self.extracted_data[index]:
                f.write(str(entry) + '\n')
            f.close()
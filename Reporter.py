from prettytable import PrettyTable
import Settings
import os
import datetime

class Reporter:

    def __init__(self, year, lon, lat, station_list, missing_dates, missing_entries, data_list):
        self.year = year
        self.lon = lon
        self.lat = lat
        self.station_list = station_list
        self.missing_dates = missing_dates
        self.missing_entries = missing_entries
        self.data_list = data_list

        self.generate_report()

    def generate_report(self):

        #Checking if the reports/ folder exists. If not, creating it
        if not os.path.isdir('reports/'):
            os.mkdir('reports/')

        # Creating new folder with the name of current timestamp in the reports/ directory
        current_date_ts = datetime.datetime.now()
        current_date = current_date_ts.strftime('%Y%m%d - %H%M%S')

        dirpath = 'reports/' + current_date + '/'
        if not os.path.isdir(dirpath):
            os.mkdir(dirpath)
            # os.mkdir(dirpath + 'therakles/')

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
        f = open(dirpath+'00_report.txt','a')
        f.write(report_text)
        f.write(str(table))

        #Writing in the report file number of missing entries in the original data set for each climate  element
        for index,station in enumerate(self.station_list):
            report_text = ('\nSuccesfully extracted data for '+station[0]+'\n'
                +'There are %i missing hour entries in the original data set \n' % self.missing_entries[index])
            f.write(report_text)
        f.close()

        #Writing in the 00_missing_values.txt file, all the time periods with missing entries in the original data set
        f = open(dirpath + '00_missing_values.txt', 'a')

        for index,list in enumerate(self.missing_dates):
            f.write(Settings.observedCharacteristics[index][0]+'\n')
            for item in list:
                f.write(str(item)+'\n')
            f.write('\n')
        f.close()

        #Creating a txt file for each data element that contains all the values extracted and later calculated in the
        #course of running the program
        for index,station in enumerate(self.station_list):
            char_name = station[0]
            filepath = dirpath + char_name+'.txt'
            f = open(filepath,'a')
            for entry in self.data_list[index]:
                f.write(str(entry)+'\n')
            f.close()

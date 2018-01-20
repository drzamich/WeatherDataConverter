from prettytable import PrettyTable
import Settings
import os
import datetime

class Reporter:
    def generate_report_raw_data(self,year,lon,lat,station_list,missing_dates,missing_entries,data_list):

        current_date_ts = datetime.datetime.now()
        current_date = current_date_ts.strftime('%Y%m%d - %H%M%S')

        dirpath = 'reports/' + current_date + '/'
        if not os.path.isdir(dirpath):
            os.mkdir(dirpath)
            # os.mkdir(dirpath + 'therakles/')

        table = PrettyTable(['Char', 'Short', 'ID', 'DateStart', 'DateEnd', 'Elev.', 'Lat.', 'Lon.', 'City', 'Bundesland'])
        for station in station_list:
            table.add_row(station)

        report_text = ('Data extraction executed at %s \n' % str(datetime.datetime.now())
        +'Choosen year: %s \n' %str(year)
        +'Latitude: %s \n' %str(lat)
        +'Lognitude: %s \n\n'%str(lon)
        +'List of most favourable weather stations: \n')

        f = open(dirpath+'00_report.txt','a')
        f.write(report_text)
        f.write(str(table))

        for index,station in enumerate(station_list):
            report_text = ('\nSuccesfully extracted and interpolated data for '+station[0]+'\n'
                +'There are %i missing hour entries in the original data set \n' % missing_entries[index])
            f.write(report_text)
        f.close()

        f = open(dirpath + '00_missing_values.txt', 'a')

        for index,list in enumerate(missing_dates):
            f.write(Settings.observedCharacteristics[index][0]+'\n')
            for item in list:
                f.write(str(item)+'\n')
            f.write('\n')
        f.close()

        for index,station in enumerate(station_list):
            filepath = dirpath + station[0]+'.txt'
            f = open(filepath,'a')
            for entry in data_list[index]:
                f.write(str(entry)+'\n')
            f.close()

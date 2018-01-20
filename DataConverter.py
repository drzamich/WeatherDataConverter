import Settings
import datetime
import calendar
import Irradiance
import math

fmt = Settings.fmt

class DataConverter:
    def __init__(self,year,raw_data):
        self.raw_data = raw_data
        self.year = year
        self.missing_list =[]
        self.missing_entries_list = []
        self.convert_data()
        self.converted_data = self.raw_data


    def convert_data(self):
        self.remove_duplicates()
        self.insert_missing_dates()
        self.strip_leap_year()
        self.convert_solar_data()


    def remove_duplicates(self):
        for data_list in self.raw_data:
            for index, item in enumerate(data_list):
                if index != 0:
                    date1 = data_list[index - 1][0]
                    date2 = data_list[index][0]
                    if date1 == date2:
                        data_list.pop(index)

    def insert_missing_dates(self):
        for data_list in self.raw_data:
            missing_list_entry = []
            missing_entries = 0
            size = len(data_list[0])

            for index, entry in enumerate(data_list):

                if index == 0:
                    if not data_list[0][0].endswith('010100'):
                        missing_entries += 1
                        new_entry = [-999] * size
                        missing_list_entry.append('before')
                        missing_list_entry.append(data_list[0][0])

                        year = data_list[0][0][0:4]
                        new_date = year + '010100'
                        new_entry[0] = new_date
                        data_list.insert(0, new_entry)

                elif index != 0 and index != (len(data_list) - 1):
                    date1 = data_list[index - 1][0]
                    date2 = data_list[index][0]
                    tstamp1 = datetime.datetime.strptime(date1, fmt)
                    tstamp2 = datetime.datetime.strptime(date2, fmt)

                    td = tstamp2 - tstamp1

                    td_hours = td.total_seconds() / 3600

                    # if the time diff between dates is bigger than 1, that means there is a missing value
                    if td_hours > 1.0:
                        missing_entries += td_hours
                        missing_list_entry.append([date1, date2])
                        # inserting calculated values to the original list
                        for x in range(1, int(td_hours)):
                            tstamp_new = tstamp1 + datetime.timedelta(hours=x)

                            date_new = datetime.datetime.strftime(tstamp_new, fmt)

                            # for some reason this cannot be defined "higher". otherwise all the missing entries have the same
                            # date like the last missing one
                            new_entry = [-999] * size
                            new_entry[0] = date_new
                            data_list.insert((index - 1) + x, new_entry)

                elif index == (len(data_list) - 1):
                    last_date = data_list[len(data_list) - 1][0]
                    if not str(last_date).endswith('123123'):
                        missing_list_entry.append('after:')
                        missing_list_entry.append(last_date)
                        tstamp1 = datetime.datetime.strptime(last_date, fmt)
                        tstamp_new = tstamp1
                        while True:
                            new_entry = [-999] * size
                            a = 1
                            tstamp_new = tstamp_new + datetime.timedelta(hours=a)
                            newdate = datetime.datetime.strftime(tstamp_new, fmt)
                            new_entry[0] = newdate
                            data_list.insert(len(data_list) + 1, new_entry)
                            a += 1
                            missing_entries += 1
                            if newdate.endswith('123123'): break

            self.missing_entries_list.append(missing_entries)
            self.missing_list.append(missing_list_entry)

    def strip_leap_year(self):
        if calendar.isleap(self.year):
            for data_list in self.raw_data:
                boundary_date = str(self.year) + '022823'
                for item in data_list:
                    date = str(item[0])
                    tstamp1 = datetime.datetime.strptime(date, fmt)
                    tstamp2 = datetime.datetime.strptime(boundary_date, fmt)
                    if tstamp1 > tstamp2:
                        tstamp3 = tstamp1 + datetime.timedelta(days=1)
                        date_new = datetime.datetime.strftime(tstamp3, fmt)
                        item[0] = date_new

                # removing last 24 entires on the data_list
                for i in range(0, 24):
                    data_list.pop()

    def convert_solar_data(self):
        solar_data_list = self.raw_data[5]
        for index,item in enumerate(solar_data_list):
            # Calculating the global and diffuse horizontal radiation values in W/m2
            diff_hour = float(item[2])   # J/cm^2*h
            diff_instant = (10000.0/3600.0)*diff_hour  #W/m2
            diff_instant_str = "{0:.2f}".format(diff_instant)

            glob_hour = float(item[3])    # J/cm^2*h
            glob_instant = (10000.0/3600.0)*glob_hour  #W/m2
            glob_instant_str = "{0:.2f}".format(glob_instant)

            item.append(diff_instant_str)   #item[6]
            item.append(glob_instant_str)   #item[7]

            #Calculating the direct normal radiation
            day_of_year = math.ceil(index+1/24.0)
            zenith = float(item[5])

            dir_nor = Irradiance.disc(glob_instant,zenith,day_of_year)
            direct_instant = dir_nor['dni']
            direct_instant_str = "{0:.2f}".format(direct_instant)
            item.append(direct_instant_str)





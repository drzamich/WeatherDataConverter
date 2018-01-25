import Settings
import datetime
import calendar
import Irradiance
import math

fmt = Settings.fmt

class DataConverter:
    """
    This clas is responsible for converting raw weater data set and calculating new values therefore preparing
    them for saving in the output file.
    """
    def __init__(self,year,raw_data):
        """
        :param year: year for which the weather data is needed
        :param raw_data: set of raw data sets
        """
        self.raw_data = raw_data
        self.year = year
        self.missing_list =[]           #list that contains data periods missing from raw data sets
        self.missing_entries_list = []  #list that contains numbers of entries missing from raw data sets
        self.convert_data()
        self.converted_data = self.raw_data


    def convert_data(self):
        #Removing duplicated entries (entries with same dates)
        self.remove_duplicates()

        #Inserting entries for which no entries exist in the original data set (values marked as missing: -999)
        self.insert_missing_dates()

        #Removing extra entries for leap year (continous set, no gaps!)
        self.strip_leap_year()

        #Converting and calculating values of irradiance
        self.convert_solar_data()

    def remove_duplicates(self):
        """
        Function responsible for removing duplicated entries (entries with same dates)
        :return: data set with only one entry per hour
        """
        for data_list in self.raw_data:
            for index, item in enumerate(data_list):
                if index != 0:
                    date1 = data_list[index - 1][0]
                    date2 = data_list[index][0]
                    #If dates of two entries in a row are the same
                    if date1 == date2:
                        #Deleting one of them
                        data_list.pop(index)

    def insert_missing_dates(self):
        """
        Function responsible for inserting entries for which no entries exist in the original data set
        (values marked as missing: -999)
        :return: data set with continous entries (there exist an entry for each hour of the year)
        """
        for data_list in self.raw_data:
            missing_list_entry = []  #list for storing missing entries' time periods
            missing_entries = 0      #variable for stroring number of missing entries
            size = len(data_list[0]) #number of columns in the data set

            for index, entry in enumerate(data_list):

                if index == 0:
                    #For the first entry on the list it is checked if it's date is 01 Jan YYYY 00:00
                    #If the date does not end with specific string, it means that the first entry has different date
                    if not data_list[0][0].endswith('010100'):
                        #Adding 1 to the missing entries number
                        missing_entries += 1
                        new_entry = [-999] * size   #new entry has all values in all columns except first (the one that
                                                    #stores the date set to -999 (marked as missing)

                        #Saving in the list with missing time ranges infromation about the time range
                        missing_list_entry.append('before')
                        missing_list_entry.append(data_list[0][0])

                        #Inserting the date of 1th Jan of given year to the new entry in the 1st column
                        year = data_list[0][0][0:4]
                        new_date = year + '010100'
                        new_entry[0] = new_date
                        #Inserting the new entry to the original list
                        data_list.insert(0, new_entry)

                elif index != 0 and index != (len(data_list) - 1):
                    #For entries that aren't 1st or last on the list, it is checked a time difference between two
                    #neighbouring entries
                    date1 = data_list[index - 1][0]
                    date2 = data_list[index][0]
                    tstamp1 = datetime.datetime.strptime(date1, fmt)
                    tstamp2 = datetime.datetime.strptime(date2, fmt)

                    #Calculating time difference in hours
                    td = tstamp2 - tstamp1
                    td_hours = td.total_seconds() / 3600

                    # if the time diff between dates is bigger than 1 hour, that means there is a missing value
                    if td_hours > 1.0:
                        # adding number of missing entries to the reporting variables
                        missing_entries += td_hours
                        missing_list_entry.append([date1, date2])

                        # for each missing entry, a new entry is created
                        for x in range(1, int(td_hours)):
                            #calculating the new date
                            tstamp_new = tstamp1 + datetime.timedelta(hours=x)
                            date_new = datetime.datetime.strftime(tstamp_new, fmt)

                            # new entry has all values in all columns except first (the one that
                            # stores the date set to -999 (marked as missing)
                            new_entry = [-999] * size

                            #Inserting new date in the first column of the new entry
                            new_entry[0] = date_new

                            #Inserting new entry in the original data set
                            data_list.insert((index - 1) + x, new_entry)

                elif index == (len(data_list) - 1):
                    #For the last element on the list it is checked if it's date is 31st Dec YYYY 23:00
                    last_date = data_list[len(data_list) - 1][0]
                    #If the last date does not end with specific string, that means that the last entry has
                    #different date
                    if not str(last_date).endswith('123123'):
                        #Ssving the missing entries time range to the reporting list
                        missing_list_entry.append('after:')
                        missing_list_entry.append(last_date)
                        tstamp1 = datetime.datetime.strptime(last_date, fmt)
                        tstamp_new = tstamp1
                        while True:
                            #Adding one hour to the last date on the data list and setting it as date of the new entry
                            #As long as the new date won't be 31st Dec YYYY 23:00

                            # new entry has all values in all columns except first (the one that
                            # stores the date set to -999 (marked as missing)
                            new_entry = [-999] * size
                            a = 1
                            tstamp_new = tstamp_new + datetime.timedelta(hours=a)
                            newdate = datetime.datetime.strftime(tstamp_new, fmt)

                            #Inserting new date in the first column of the new entry
                            new_entry[0] = newdate

                            #Inserting new entry in the original data set
                            data_list.insert(len(data_list) + 1, new_entry)
                            a += 1
                            missing_entries += 1

                            #Breaking the loop when reaching last hour of the year
                            if newdate.endswith('123123'): break

            self.missing_entries_list.append(missing_entries)
            self.missing_list.append(missing_list_entry)

    def strip_leap_year(self):
        """
        Function responsible for removine excessive number of entries from the data set which results from the fact
        that the given year is a leap year. For all entries with dates after 23:00 28th Feb, one day is added to the
        original date. Finally the last 24 entries (originally from 31st Dec) are removed from the list.
        :return: continous(without gap that would result from removing entries from 29th Feb from the data set)
                    data set with 8760 (365*24) entries
        """
        if calendar.isleap(self.year):
            for data_list in self.raw_data:
                boundary_date = str(self.year) + '022823'  #boundary date is the 23:00 28th Feb
                for item in data_list:
                    date = str(item[0])
                    tstamp1 = datetime.datetime.strptime(date, fmt)
                    tstamp2 = datetime.datetime.strptime(boundary_date, fmt)
                    if tstamp1 > tstamp2:
                        #for each entry with date after the boundary date
                        #one day is added to the original date, therefore moving all entries one day forward
                        tstamp3 = tstamp1 + datetime.timedelta(days=1)
                        date_new = datetime.datetime.strftime(tstamp3, fmt)
                        item[0] = date_new

                # removing last 24 entires on the data_list, therefore limiting number of entries to 8760
                for i in range(0, 24):
                    data_list.pop()

    def convert_solar_data(self):
        """
        Function responsible for calculating values regarding solar irradiance
        :return: data set with calculated additional values
        """
        solar_data_list = self.raw_data[5]
        for index,item in enumerate(solar_data_list):
            # Calculating the global and diffuse horizontal radiation values in W/m2
            #The original unit is J/cm^2*h

            #Diffuse horizontal irradiance
            diff_hour = float(item[2])   # J/cm^2*h
            diff_instant = (10000.0/3600.0)*diff_hour  #W/m2
            diff_instant_str = "{0:.2f}".format(diff_instant)

            #Global horizontal irradiance
            glob_hour = float(item[3])    # J/cm^2*h
            glob_instant = (10000.0/3600.0)*glob_hour  #W/m2
            glob_instant_str = "{0:.2f}".format(glob_instant)

            #Adding calculated values to the list
            item.append(diff_instant_str)   #item[6]
            item.append(glob_instant_str)   #item[7]

            #Calculating the direct normal irradiance
            day_of_year = math.ceil(index+1/24.0)
            zenith = float(item[5])

            #Calculating the direct normal irradiance using the disc() method of the Irradiance module
            dir_nor = Irradiance.disc(glob_instant,zenith,day_of_year)
            # the value of direct normal irradiance is saved in the dir_nor table under the key 'dni'
            direct_instant = dir_nor['dni']
            direct_instant_str = "{0:.2f}".format(direct_instant) #formatting the float number

            #adding the calculated value to the list
            item.append(direct_instant_str)

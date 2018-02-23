import Settings
import datetime
import calendar
import Irradiance
import math
import pickle

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
        self.calculate_data()
        self.converted_data = self.raw_data


    def convert_data(self):
        #Removing duplicated entries (entries with same dates)
        print('-Remove duplicates')
        self.remove_duplicates()

        #Inserting entries for which no entries exist in the original data set (values marked as missing: -999)
        print('-Insert missing dates')
        self.insert_missing_dates()

        print('-Interpolate data')
        self.interpolate_data()

        #Removing extra entries for leap year (continous set, no gaps!)
        print('-Strip leap year')
        self.strip_leap_year()


    def calculate_data(self):

        #Converting and calculating values for temperature and relative humidity
        print('-Convert air temp data')
        self.convert_air_temperature_data()

        # Converting and calculating values for pressure
        print('-Convert pressure data')
        self.convert_pressure_data()

        #Converting and calculating values of irradiance
        print('-Convert solar data')
        self.convert_solar_data()

        #Converting values of cloudiness from oktas to tenths
        print('-Convert cloudiness data')
        self.convert_cloudiness_data()

        print('-Convert wind data')
        self.convert_wind_data()

        print('-Calculate horizontal infrared')
        self.calculate_horizontal_infrared()


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
                        missing_list_entry.append('before:')
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

    def interpolate_data(self):
        for index,data in enumerate(self.raw_data):

            #Saving indexes of rows with missing data
            #This is done for each column separately
            missing_values = [[]]
            for i, row in enumerate(data):
                for column, item in enumerate(row):
                    if float(item) == -999.0:
                        if len(missing_values) == column:
                            missing_values.append([i])

                        elif len(missing_values) > column:
                            missing_values[column].append(i)


            #for air temp, rel humidity, soil temperature and solar data, interpolation is made based
            #on the values from neighbouring days
            if index==0:
                self.interpolate_by_average(data,missing_values)

            #for cloudiness, precipitation, pressure and wind data, intepolation is made direcly based on the values
            #nearest to the missing data
            elif index== 3:
                self.interpolate_directly(data,missing_values)


    def interpolate_by_average(self,data,missing_values):
        for column, set in enumerate(missing_values):
            for index in set:
                #looking for indexes of entries with available data, which will be a base for interpolation
                lower_index = -1
                upper_index = 9999

                for j in range(index-24,-1,-24):
                    if j not in set:
                        lower_index = j
                        break

                for j in range(index+24,len(data),24):
                    if j not in set:
                        upper_index = j
                        break

                #set consiss all of missing values
                if lower_index == 9999 and upper_index == -1:
                    break

                #missing values at the start of set
                elif lower_index == -1 and upper_index != 9999:
                    data[index][column] = data[upper_index][column]

                #missing values at the end of the set
                elif lower_index != -1 and upper_index == 9999:
                    data[index][column] = data[lower_index][column]

                else:
                    data[index][column] = (float(data[upper_index][column]) + float(data[lower_index][column]))/2


    def interpolate_directly(self,data,missing_values):

        for column,set in enumerate(missing_values):
            for index in set:

                #looking for indexes of entries with available data, which will be a base for interpolation
                lower_index = -1
                upper_index = 9999

                for j in range(index-1,-1,-1):
                    if j not in set:
                        lower_index = j
                        break

                for j in range(index, len(data)):
                    if j not in set:
                        upper_index = j
                        break

                #set consiss all of missing values
                if lower_index == 9999 and upper_index == -1:
                    break

                #missing values at the start of set
                elif lower_index == -1 and upper_index != 9999:
                    data[index][column] = data[upper_index][column]

                #missing values at the end of the set
                elif lower_index != -1 and upper_index == 9999:
                    data[index][column] = data[lower_index][column]

                else:
                    lower_val = float(data[lower_index][column])
                    upper_val = float(data[upper_index][column])
                    diff = upper_val-lower_val

                    width = upper_index - lower_index
                    distance = index - lower_index

                    incr = diff/width

                    new_val = lower_val+incr*distance
                    new_val = format(new_val,'.1f')
                    data[index][column] = new_val


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
                tstamp2 = datetime.datetime.strptime(boundary_date, fmt)
                for item in data_list:
                    date = str(item[0])
                    tstamp1 = datetime.datetime.strptime(date, fmt)
                    if tstamp1 > tstamp2:
                        #for each entry with date after the boundary date
                        #one day is added to the original date, therefore moving all entries one day forward
                        tstamp3 = tstamp1 + datetime.timedelta(days=1)
                        date_new = datetime.datetime.strftime(tstamp3, fmt)
                        item[0] = date_new

                # removing last 24 entires on the data_list, therefore limiting number of entries to 8760
                for i in range(0, 24):
                    data_list.pop()

    def convert_air_temperature_data(self):
        air_temp_data_list = self.raw_data[0]
        for item in air_temp_data_list:

            temp = float(item[1])
            humidity = int(float(item[2]))

            mark = 0
            if temp == -999.0 or temp < -70.0 or temp > 70.0:
                dry_bulb = 99.9
                mark = 1
            else:
                dry_bulb = temp

            if humidity == -999 or humidity < 0 or humidity > 110:
                rel_humidity = 999
                mark = 1
            else:
                rel_humidity = humidity

            if mark == 1:
                dew_point = 99.9
            elif mark == 0:
                dew_point = self.dew_point_temperature(temp,humidity)


            item.append(dry_bulb)       #item[3]
            item.append(dew_point)      #item[4]
            item.append(rel_humidity)   #item[5]

    def convert_pressure_data(self):
        pressure_data = self.raw_data[3]
        for item in pressure_data:
            press = int(float(item[2]))*100 #[Pa]

            if press > 120000 or press < 31000 or press == -999:
                atm_pressure =  999999
            else:
                atm_pressure = press

            item.append(atm_pressure)

    def convert_wind_data(self):
        wind_data = self.raw_data[7]
        for item in wind_data:
            speed = float(item[1])
            speed = int(round(speed,0))
            dir = int(float(item[2]))
            dir = int(0.9*dir)  #grad to degree

            if dir <0 or dir >360 or dir == -999:
                wind_dir = 999
            else:
                wind_dir = dir

            if speed < 0 or speed > 40 or speed == -999:
                wind_speed = 999
            else:
                wind_speed = speed

            item.append(wind_dir)
            item.append(wind_speed)

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
            diff_instant = int(round(diff_instant,0))

            #Global horizontal irradiance
            glob_hour = float(item[3])    # J/cm^2*h
            glob_instant = (10000.0/3600.0)*glob_hour  #W/m2
            glob_instant = int(round(glob_instant,0))

            #Adding calculated values to the list
            item.append(diff_instant)   #item[6]
            item.append(glob_instant)   #item[7]

            #Calculating the direct normal irradiance
            day_of_year = math.ceil(index+1/24.0)
            zenith = float(item[5])

            #Calculating the direct normal irradiance using the disc() method of the Irradiance module
            dir_nor = Irradiance.disc(glob_instant,zenith,day_of_year)
            # the value of direct normal irradiance is saved in the dir_nor table under the key 'dni'
            direct_instant = dir_nor['dni']
            direct_instant = "{0:.2f}".format(direct_instant) #formatting the float number
            direct_instant = int(round(float(direct_instant),0))

            #adding the calculated value to the list
            item.append(direct_instant) #item[8]

            #When values necessary for calculation are missing from the data set, the calculated values are set as missing
            if zenith == -999.0 or diff_hour == -999.0 or glob_hour == -999.0:
                item[6] = 0
                item[8] = 0

    def convert_cloudiness_data(self):
        cloudiness_data_list = self.raw_data[1]
        for item in cloudiness_data_list:
            okta_value = int(item[1])

            if okta_value == -1 or okta_value == -999:
                tenth_value = 99 #99 means "missing" for the "Total Sky Cover field"
            elif okta_value == 0: tenth_value = 0
            elif okta_value == 1: tenth_value = 1
            elif okta_value == 2: tenth_value = 2
            elif okta_value == 3: tenth_value = 4
            elif okta_value == 4: tenth_value = 5
            elif okta_value == 5: tenth_value = 6
            elif okta_value == 6: tenth_value = 7 #7.5?
            elif okta_value == 7: tenth_value = 9 #9.5?
            elif okta_value == 8: tenth_value = 10

            item.append(tenth_value)

    def calculate_horizontal_infrared(self):
        cloudiness_data = self.raw_data[1]
        temperature_data = self.raw_data[0]
        solar_data = self.raw_data[5]

        for index,item in enumerate(cloudiness_data):
            sky_cover = item[2]
            dry_bulb = temperature_data[index][3]
            dew_point = temperature_data[index][4] + 273

            if sky_cover == 99 or dry_bulb == 99.9 or dry_bulb == '' or dew_point == 99.9:
                horizontal_infrared = 9999
            else:
                dry_bulb = temperature_data[index][3] + 273
                horizontal_infrared = self.horizontal_infrared_intensity(dry_bulb,dew_point,sky_cover)

            solar_data[index].append(horizontal_infrared)

    def dew_point_temperature(self,temp,humidity):
        """
        Taken from https://en.wikipedia.org/wiki/Dew_point#Calculating_the_dew_point
        """
        a = 6.1121
        b = 18.678
        c = 257.14
        T = temp
        RH = humidity

        gamma = math.log(RH/100) + ((b*T)/(c+T))

        T_dp = (c*gamma)/(b-gamma)
        T_dp1 = round(T_dp,1)
        return T_dp1

    def emissivity(self,dew_point,sky_cover):
        N = sky_cover
        e = (0.787+0.764*math.log(dew_point/273))*(1+0.0224*N+0.0035*N*N+0.00028*N*N*N)
        return e

    def horizontal_infrared_intensity(self,dry_bulb,dew_point,sky_cover):
        b = 5.6697*10**(-8)
        e = self.emissivity(dew_point,sky_cover)
        hor = e*b*dry_bulb**(4)
        hor = int(round(hor,0))
        return hor
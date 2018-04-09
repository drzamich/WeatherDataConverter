import calendar
import copy
import datetime
import math

from external import Irradiance
import Reporter
import Settings


class DataConverter:
    """
    This class is responsible for converting raw weather data set and calculating new values therefore preparing
    them for saving in the output file.
    """

    def __init__(self):
        print('DataConverter')
        Reporter.set_status('Converting data...', 21)
        self.converted_data = copy.deepcopy(Reporter.extracted_data)  # making a deep copy of raw data
        self.year = Settings.year
        self.missing_list = []  # list that contains data periods missing from raw data sets
        self.missing_entries_list = []  # list that contains numbers of entries missing from raw data sets
        self.prepare_data()
        self.calculate_data()

        Reporter.converted_data = self.converted_data
        Reporter.missing_list = self.missing_list
        Reporter.missing_entries_list = self.missing_entries_list

    def prepare_data(self):
        """
        Set of functions that prepare raw set of data extracted from the stations but do not convert or
        recalculate them in any way.
        """

        # Removing duplicated entries (entries with same dates)
        print('-Remove duplicates')
        Reporter.set_status('Converting data... removing duplicates', 25)
        self.remove_duplicates()

        # Inserting entries for which no entries exist in the original data set (values marked as missing: -999)
        print('-Insert missing dates')
        Reporter.set_status('Converting data... inserting missing dates', 27)
        self.insert_missing_dates()

        # Saving extracted data set (before interpolation) for future saving in the report file
        Reporter.extracted_data = copy.deepcopy(self.converted_data)

        print('-Interpolate data')
        if Settings.interpolate_data:
            Reporter.set_status('Converting data... searching missing values and data interpolation', 30)
        else:
            Reporter.set_status('Converting data... searching missing values', 30)
        self.interpolate_data()

        # Removing extra entries for leap year (continous set, no gaps!)
        print('-Strip leap year')
        Reporter.set_status('Converting data... stripping leap year', 40)
        self.strip_leap_year()

    def calculate_data(self):
        """
        Set of functions that reformat and recalculate values of climate elements therefore to state needed by the epw
        file format.
        """
        # Converting and calculating values for temperature and relative humidity
        print('-Convert air temp data')
        Reporter.set_status('Calculating data... air temperature', 42)
        self.convert_air_temperature_data()

        # Converting and calculating values for pressure
        print('-Convert pressure data')
        Reporter.set_status('Calculating data... pressure', 44)
        self.convert_pressure_data()

        # Converting and calculating values of irradiance
        print('-Convert solar data')
        Reporter.set_status('Calculating data... solar data', 46)
        self.convert_solar_data()

        # Converting values of cloudiness from oktas to tenths
        print('-Convert cloudiness data')
        Reporter.set_status('Calculating data... cloudiness', 50)
        self.convert_cloudiness_data()

        # Converting values of wind data
        print('-Convert wind data')
        Reporter.set_status('Calculating data... wind', 54)
        self.convert_wind_data()

        # Calculating values of horizontal infrared irradiance
        print('-Calculate horizontal infrared')
        Reporter.set_status('Calculating data... horizontal infrared', 56)
        self.calculate_horizontal_infrared()

    def remove_duplicates(self):
        """
        Function responsible for removing duplicated entries (entries with same dates)
        :return: data set with only one entry per hour
        """
        for data_list in self.converted_data:
            for index, item in enumerate(data_list):
                if index != 0:
                    date1 = data_list[index - 1][0]
                    date2 = data_list[index][0]
                    # If dates of two entries in a row are the same
                    if date1 == date2:
                        # Deleting one of them
                        data_list.pop(index)

    def insert_missing_dates(self):
        """
        Function responsible for inserting entries for which no entries exist in the original data set
        (values marked as missing: -999)
        :return: data set with continous entries (there exist an entry for each hour of the year)
        """
        fmt = Settings.fmt  # date format
        for char_index, data_list in enumerate(self.converted_data):
            size = len(data_list[0])  # number of columns in the data set

            for index, entry in enumerate(data_list):

                if index == 0:
                    # For the first entry on the list it is checked if it's date is 01 Jan YYYY 00:00
                    # If the date does not end with specific string, it means that the first entry has different date
                    if not data_list[0][0].endswith('010100'):
                        # Inserting the date of 1th Jan of given year to the new entry in the 1st column
                        year = data_list[0][0][0:4]
                        new_date = year + '010100'

                        # new entry has all values in all columns except first (the one that
                        # stores the date set to -999 (marked as missing)
                        new_entry = [-999] * size

                        # In case for sunshine duration (sun) data, where data between 21 and 02 is always
                        # missing, setting the value to 0.00
                        if char_index == 6 and new_date.endswith(('21', '22', '23', '00', '01', '02')):
                            new_entry = [0.00] * size

                        # Inserting date in the new entry
                        new_entry[0] = new_date

                        # Inserting the new entry to the original list
                        data_list.insert(0, new_entry)

                elif index != 0 and index != (len(data_list) - 1):
                    # For entries that aren't 1st or last on the list, it is checked a time difference between two
                    # neighbouring entries
                    date1 = data_list[index - 1][0]
                    date2 = data_list[index][0]
                    tstamp1 = datetime.datetime.strptime(date1, fmt)
                    tstamp2 = datetime.datetime.strptime(date2, fmt)

                    # Calculating time difference in hours
                    td = tstamp2 - tstamp1
                    td_hours = td.total_seconds() / 3600

                    # If the time diff between dates is bigger than 1 hour, that means there is a missing value
                    if td_hours > 1.0:
                        # for each missing entry, a new entry is created
                        for x in range(1, int(td_hours)):
                            # calculating the new date
                            tstamp_new = tstamp1 + datetime.timedelta(hours=x)
                            new_date = datetime.datetime.strftime(tstamp_new, fmt)

                            # new entry has all values in all columns except first (the one that
                            # stores the date set to -999 (marked as missing)
                            new_entry = [-999] * size

                            # In case for sunshine duration (sun) data, where data between 21 and 02 is always
                            # missing, setting the value to 0.00
                            if char_index == 6 and new_date.endswith(('21', '22', '23', '00', '01', '02')):
                                new_entry = [0.00] * size

                            # Inserting new date in the first column of the new entry
                            new_entry[0] = new_date

                            # Inserting new entry in the original data set
                            data_list.insert((index - 1) + x, new_entry)

                elif index == (len(data_list) - 1):
                    # For the last element on the list it is checked if it's date is 31st Dec YYYY 23:00
                    last_date = data_list[len(data_list) - 1][0]
                    # If the last date does not end with specific string, that means that the last entry has
                    # different date
                    if not str(last_date).endswith('123123'):
                        # Saving the missing entries time range to the reporting list
                        tstamp1 = datetime.datetime.strptime(last_date, fmt)
                        tstamp_new = tstamp1
                        while True:
                            # Adding one hour to the last date on the data list and setting it as date of the new entry
                            # As long as the new date won't be 31st Dec YYYY 23:00

                            a = 1
                            tstamp_new = tstamp_new + datetime.timedelta(hours=a)
                            new_date = datetime.datetime.strftime(tstamp_new, fmt)

                            # new entry has all values in all columns except first (the one that
                            # stores the date) set to -999 (marked as missing)
                            new_entry = [-999] * size

                            # In case for sunshine duration (sun) data, where data between 21 and 02 is always
                            # missing, setting the value to 0.00
                            if char_index == 6 and new_date.endswith(('21', '22', '23', '00', '01', '02')):
                                new_entry = [0.00] * size

                            # Inserting new date in the first column of the new entry
                            new_entry[0] = new_date

                            # Inserting new entry in the original data set
                            data_list.insert(len(data_list) + 1, new_entry)
                            a += 1

                            # Breaking the loop when reaching last hour of the year
                            if new_date.endswith('123123'):
                                break

    def interpolate_data(self):
        """
        Function that exchanges missing values in the data set with values interpolated either based on nearest
        non-missing values (interpolate_directly()) or non-missing values in a 24h distance (interpolate_by_average())
        """
        for index, data in enumerate(self.converted_data):
            missing_entries = 0
            missing_dates = []
            # Saving indexes of rows with missing data
            # This is done for each column separately
            missing_values = [[]]
            for i, row in enumerate(data):
                for column, item in enumerate(row):
                    # The value is perceived as missing when it's value is set to -999
                    # For cloudiness (index==1) missing observations are also marked with -1
                    # Exception is also made for soil_temperature at 2cm depth (always missing)
                    if float(item) == -999 and not (index == 4 and column == 1) or (float(item) == -1.0 and index == 1):

                        if len(missing_values) == column:  # there is already sub-list for this column in the main list
                            missing_values.append([i])
                        elif len(missing_values) > column:
                            missing_values[column].append(i)

                        missing_entries += 1
                        date = row[0]
                        if date not in missing_dates:
                            missing_dates.append(date)

            self.missing_list.append(missing_dates)
            self.missing_entries_list.append(missing_entries)

            if Settings.interpolate_data:
                # for air temp, rel humidity, soil temperature and solar data, interpolation is made based
                # on the values from neighbouring days
                if index == 0 or index == 4 or index == 5:
                    self.interpolate_by_average(data, missing_values)

                # for cloudiness, precipitation, pressure and wind data, interpolation is directly based on the values
                # nearest to the missing data
                elif index == 1 or index == 2 or index == 3 or index == 6 or index == 7:
                    self.interpolate_directly(data, missing_values, index)

    def interpolate_by_average(self, data, missing_values):
        """
        Function inserts new values in place of missing values.
        The new value is the average of value at the same time one day before and one day later.
        """
        for column, set in enumerate(missing_values):
            for index in set:
                # looking for indexes of entries with available data, which will be a base for interpolation
                lower_index = -1
                upper_index = 9999

                for j in range(index - 24, -1, -24):
                    if j not in set:
                        lower_index = j
                        break

                for j in range(index + 24, len(data), 24):
                    if j not in set:
                        upper_index = j
                        break

                # set consists all of missing values
                if lower_index == -1 and upper_index == 9999:
                    break

                # missing values at the start of set
                # new value is equal to the next non-missing value (24h gap)
                elif lower_index == -1 and upper_index != 9999:
                    data[index][column] = data[upper_index][column]

                # missing values at the end of the set
                # new value is equal to the last non-missing value (24h gap)
                elif lower_index != -1 and upper_index == 9999:
                    data[index][column] = data[lower_index][column]

                # missing values in the middle of the set
                else:
                    data[index][column] = (float(data[upper_index][column]) + float(data[lower_index][column])) / 2

    def interpolate_directly(self, data, missing_values, char_index):
        """
        Function inserts new values in place of missing values.
        The new is calculated as a result of direct interpolation between neighbouring non-missing values.
        """
        for column, set in enumerate(missing_values):
            for index in set:

                # looking for indexes of entries with available data, which will be a base for interpolation
                lower_index = -1
                upper_index = 9999

                for j in range(index - 1, -1, -1):
                    if j not in set:
                        lower_index = j
                        break

                for j in range(index, len(data)):
                    if j not in set:
                        upper_index = j
                        break

                # set consists all of missing values
                if lower_index == -1 and upper_index == 9999:
                    break  # do nothing

                # missing values at the start of set
                # new value is equal to the first non-missing value
                elif lower_index == -1 and upper_index != 9999:
                    data[index][column] = data[upper_index][column]

                # missing values at the end of the set
                # new value is equal to the last non-missing value
                elif lower_index != -1 and upper_index == 9999:
                    data[index][column] = data[lower_index][column]

                # missing values in the middle of the set
                else:
                    lower_val = float(data[lower_index][column])
                    upper_val = float(data[upper_index][column])
                    diff = upper_val - lower_val

                    width = upper_index - lower_index
                    distance = index - lower_index

                    incr = diff / width

                    new_val = lower_val + incr * distance
                    new_val = format(new_val, '.1f')
                    if char_index == 1:  # special case for cloudiness data
                        new_val = int(round(float(new_val)))
                    data[index][column] = new_val

    def strip_leap_year(self):
        """
        Function responsible for removing excessive number of entries from the data set which results from the fact
        that the given year is a leap year. For all entries with dates after 23:00 28th Feb, one day is added to the
        original date. Finally the last 24 entries (originally from 31st Dec) are removed from the list.
        :return: continuous(without gap that would result from removing entries from 29th Feb from the data set)
                    data set with 8760 (365*24) entries
        """
        fmt = Settings.fmt
        if calendar.isleap(self.year):
            for data_list in self.converted_data:
                boundary_date = str(self.year) + '022823'  # boundary date is the 23:00 28th Feb
                tstamp2 = datetime.datetime.strptime(boundary_date, fmt)
                for item in data_list:
                    date = str(item[0])
                    tstamp1 = datetime.datetime.strptime(date, fmt)
                    if tstamp1 > tstamp2:
                        # for each entry with date after the boundary date
                        # one day is added to the original date, therefore moving all entries one day forward
                        tstamp3 = tstamp1 + datetime.timedelta(days=1)
                        date_new = datetime.datetime.strftime(tstamp3, fmt)
                        item[0] = date_new

                # removing last 24 entries on the data_list, therefore limiting number of entries to 8760
                for i in range(0, 24):
                    data_list.pop()

    def convert_air_temperature_data(self):
        """
        Function prepares air temperature air relative humidity data (formatting) and
        based on that, calculates Dew Point Temperatures.
        :return:
        """
        air_temp_data_list = self.converted_data[0]
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

            if mark == 1:  # if mark is set to one that means its not possible to calculate dew point temp
                dew_point = 99.9
            elif mark == 0:
                dew_point = self.dew_point_temperature(temp, humidity)

            item.append(dry_bulb)  # item[3]
            item.append(dew_point)  # item[4]
            item.append(rel_humidity)  # item[5]

    def convert_pressure_data(self):
        """
        Function prepares pressure data (formatting).
        """
        pressure_data = self.converted_data[3]
        for item in pressure_data:
            press = int(float(item[2])) * 100  # [Pa]

            if press > 120000 or press < 31000 or press == -999:
                atm_pressure = 999999
            else:
                atm_pressure = press

            item.append(atm_pressure)

    def convert_wind_data(self):
        """
        Function prepares wind data (conversion from Grad to degrees, formatting).
        """
        wind_data = self.converted_data[7]
        for item in wind_data:
            speed = float(item[1])
            speed = int(round(speed, 0))
            direction = int(float(item[2]))
            direction = int(0.9 * direction)  # grad to degree

            if direction < 0 or direction > 360 or direction == -999:
                wind_dir = 999
            else:
                wind_dir = direction

            if speed < 0 or speed > 40 or speed == -999:
                wind_speed = 999
            else:
                wind_speed = speed

            item.append(wind_dir)
            item.append(wind_speed)

    def convert_solar_data(self):
        """
        Function responsible for calculating values regarding solar irradiance.
        :return: data set with calculated additional values
        """
        solar_data_list = self.converted_data[5]
        for index, item in enumerate(solar_data_list):
            # Calculating the global and diffuse horizontal radiation values in W/m2
            # The original unit is J/cm^2*h

            # Diffuse horizontal irradiance
            diff_hour = float(item[2])  # J/cm^2*h
            diff_instant = (10000.0 / 3600.0) * diff_hour  # W/m2
            diff_instant = int(round(diff_instant, 0))

            # Global horizontal irradiance
            glob_hour = float(item[3])  # J/cm^2*h
            glob_instant = (10000.0 / 3600.0) * glob_hour  # W/m2
            glob_instant = int(round(glob_instant, 0))

            # Adding calculated values to the list
            item.append(diff_instant)  # item[6]
            item.append(glob_instant)  # item[7]

            # Calculating the direct normal irradiance
            day_of_year = math.ceil(index + 1 / 24.0)
            zenith = float(item[5])

            # Calculating the direct normal irradiance using the disc() method of the Irradiance module
            dir_nor = Irradiance.disc(glob_instant, zenith, day_of_year)
            # the value of direct normal irradiance is saved in the dir_nor table under the key 'dni'
            direct_instant = dir_nor['dni']
            direct_instant = "{0:.2f}".format(float(direct_instant))  # formatting the float number
            direct_instant = int(round(float(direct_instant), 0))

            # adding the calculated value to the list
            item.append(direct_instant)  # item[8]

            # When values necessary for calculation are missing from the data set, the calculated values are set
            # as missing
            if zenith == -999.0 or diff_hour == -999.0 or glob_hour == -999.0:
                item[6] = 0
                item[8] = 0

    def convert_cloudiness_data(self):
        """
        Function prepares cloudiness data (conversion from oktas to tenths).
        """
        cloudiness_data_list = self.converted_data[1]
        for item in cloudiness_data_list:
            okta_value = int(item[1])

            if okta_value == -1 or okta_value == -999:
                tenth_value = 99  # 99 means "missing" for the "Total Sky Cover field"
            elif okta_value == 0:
                tenth_value = 0
            elif okta_value == 1:
                tenth_value = 1
            elif okta_value == 2:
                tenth_value = 2
            elif okta_value == 3:
                tenth_value = 4
            elif okta_value == 4:
                tenth_value = 5
            elif okta_value == 5:
                tenth_value = 6
            elif okta_value == 6:
                tenth_value = 7  # 7.5?
            elif okta_value == 7:
                tenth_value = 9  # 9.5?
            elif okta_value == 8:
                tenth_value = 10

            item.append(tenth_value)

    def calculate_horizontal_infrared(self):
        """
        Function calculates values of Horizontal Infrared Radiation Intensity based on temperature and cloudiness data.
        """
        cloudiness_data = self.converted_data[1]
        temperature_data = self.converted_data[0]
        solar_data = self.converted_data[5]

        for index, item in enumerate(cloudiness_data):
            sky_cover = item[2]
            dry_bulb = temperature_data[index][3]
            dew_point = temperature_data[index][4] + 273

            if sky_cover == 99 or dry_bulb == 99.9 or dry_bulb == '' or dew_point == 99.9:
                horizontal_infrared = 9999
            else:
                dry_bulb = temperature_data[index][3] + 273
                horizontal_infrared = self.horizontal_infrared_intensity(dry_bulb, dew_point, sky_cover)

            solar_data[index].append(horizontal_infrared)

    def dew_point_temperature(self, temp, humidity):
        """
        Function calculates dew point temperature [*C] based on dry bulb temperature [*C] and rel. humidity [%]
        Taken from https://en.wikipedia.org/wiki/Dew_point#Calculating_the_dew_point
        """
        a = 6.1121
        b = 18.678
        c = 257.14
        t = temp
        r_h = humidity

        gamma = math.log(r_h / 100) + ((b * t) / (c + t))

        t_dp = (c * gamma) / (b - gamma)
        t_dp1 = round(t_dp, 1)
        return t_dp1

    def emissivity(self, dew_point, sky_cover):
        """
        Function calculates sky emissivity based on the dew point temperature [K] and cloudiness [tenths])
        """
        n = sky_cover
        e = (0.787 + 0.764 * math.log(dew_point / 273)) * (1 + 0.0224 * n + 0.0035 * n * n + 0.00028 * n * n * n)
        return e

    def horizontal_infrared_intensity(self, dry_bulb, dew_point, sky_cover):
        """
        Function calculates Horizontal Infrared Radiation Intensity [W/m2] based on dry bulb temp. [K],
        dew point temp [K] and sky cover [tenths]
        """
        b = 5.6697 * 10 ** (-8)
        e = self.emissivity(dew_point, sky_cover)
        hor = e * b * dry_bulb ** 4
        hor = int(round(hor, 0))
        return hor

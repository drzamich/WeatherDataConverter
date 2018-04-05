import Reporter
import Settings


class DataOutputer:
    """
    This class, given the prepared sets of climate data, prepares the EPW file for use in other programs.
    """
    def __init__(self):
        print('Outputer')
        Reporter.set_status('Writing data', 70)
        self.converted_data = Reporter.converted_data
        self.station_list = Reporter.station_list
        self.year = Settings.year
        self.lon = str(Settings.lon)
        self.lat = str(Settings.lat)
        self.output_path = Settings.output_path
        self.default_set = []

        # The variable containing characteristics of all fields that are present in the EPW file
        self.fields = [
            # [field_number, field_name, default (missing)_value, flag_missing, flag_available, uncertainty,
            # data_set_table, table_column]
            [1, 'Year', '1980', '', '', '', 999, 999],
            [2, 'Month', '1', '', '', '', 999, 999],
            [3, 'Day', '1', '', '', '', 999, 999],
            [4, 'Hour', '1', '', '', '', 999, 999],
            [5, 'Minute', '60', '', '', '', 999, 999],
            [6, 'Data source and uncertainty flags', '?0?0?0?0?0?0?0?0?0?0?0?0?0?0?0?0?0?0?0?0?0?0', '', '', '', 999,
             999],
            [7, 'Dry Bulb Temperature', '99.9', '?', 'A', '7', 0, 3],
            [8, 'Dew Point Temperature', '99.9', '?', 'E', '7', 0, 4],
            [9, 'Relative humidity', '999', '?', 'A', '7', 0, 5],
            [10, 'Atmospheric Station Pressure', '999999', '?', 'A', '7', 3, 3],
            [11, 'Extraterrestrial Horizontal Radiation', '9999', '', '', '', 999, 999],
            [12, 'Extraterrestrial Direct Normal Radiation', '9999', '', '', '', 999, 999],
            [13, 'Horizontal Infrared Radiation Intensity', '9999', '?', 'E', '0', 5, 9],
            [14, 'Global Horizontal Radiation', '9999', '?', 'A', '0', 999, 999],
            [15, 'Direct Normal Radiation', '0', '?', 'D', '0', 5, 8],
            [16, 'Diffuse Horizontal Radiation', '0', '?', 'D', '0', 5, 6],
            [17, 'Global Horizontal Illuminance', '999999', '?', 'A', '0', 999, 999],
            [18, 'Direct Normal Illuminance', '999999', '?', 'A', '0', 999, 999],
            [19, 'Diffuse Horizontal Illuminance', '999999', '?', 'A', '0', 999, 999],
            [20, 'Zenith Luminance', '9999', '?', 'A', '0', 999, 999],
            [21, 'Wind Direction', '999', '?', 'A', '0', 7, 3],
            [22, 'Wind Speed', '999', '?', 'A', '0', 7, 4],
            [23, 'Total Sky Cover', '99', '?', 'A', '0', 1, 2],
            [24, 'Opaque Sky Cover', '99', '?', 'A', '0', 999, 999],
            [25, 'Visibility', '9999', '?', 'A', '0', 999, 999],
            [26, 'Ceiling Height', '99999', '?', 'A', '0', 999, 999],
            [27, 'Present Weather Observation', '9', '', '', '', 999, 999],
            [28, 'Present Weather Codes', '999999999', '', '', '', 999, 999],
            [29, 'Precipitable Water', '999', '?', 'A', '0', 999, 999],
            [30, 'Aerosol Optical Depth', '.999', '?', 'A', '0', 999, 999],
            [31, 'Snow Depth', '999', '?', 'A', '0', 999, 999],
            [32, 'Days Since Last Snowfall', '99', '?', 'A', '0', 999, 999],
            [33, 'Albedo', '999', '', '', '', 999, 999],
            [34, 'Liquid Precipitation Depth', '999', '', '', '', 999, 999],
            [35, 'Liquid Precipitation Quantity', '99', '', '', '', 999, 999]
        ]
        self.field_number = len(self.fields)

        self.prepare_data()

    def prepare_data(self):
        # Calculate average ground temperatures
        self.prepare_soil_data()

        # Create data set with all values marked as missing
        self.create_blank_set()

        # Exchange all non-missing values in previously prepared data set
        self.fill_blank_set()

        # Modify flags for non-missing values
        self.modify_flags()

        # Prepare information for header
        self.prepare_header()

        # Save .epw file
        self.write_epw_file()

    def prepare_soil_data(self):
        """
        Function creates the string with GROUND TEMPERATURES in the .epw file.
        Specifically, it calculates average ground temperatures for different depths for each first day of the month.
        """
        soil_temperatures = self.converted_data[4]

        # Depths for which ground temperatures are recorded
        ground_temperatures_depths = [0.02, 0.05, 0.10, 0.20, 0.50, 1.0]  # m

        # Other values, left as blanks
        soil_conductivities = ['', '', '', '', '', '', '']
        soil_densities = ['', '', '', '', '', '', '']
        soil_specific_heats = ['', '', '', '', '', '', '']

        # This variable contains numbers of rows containing records from the 1st hour of each month
        gr_temp_month_begins = [0, 744, 1416, 2160, 2880, 3624, 4344, 5088, 5832, 6552, 7296, 8016]

        # Defines how missing values will be presented in the .epw file
        missing_value_mark = ''

        # Calculating ground temperature averages for each month
        averages_by_month = []
        for start_index in gr_temp_month_begins:
            month_averages = []
            for column in range(1, 7):
                sum = 0
                count = 0
                for i in range(0, 24):
                    row = start_index + i
                    temp = float(soil_temperatures[row][column])
                    if temp == -999:  # missing temperature value
                        continue
                    else:
                        count += 1
                        sum += temp

                # If all values for ground temperature were missing, no average is calculated and the temperature
                # is marked as missing
                if count != 0:
                    average = sum / count
                    average = round(average, 1)
                else:
                    average = missing_value_mark

                month_averages.append(average)
            averages_by_month.append(month_averages)

        # Sorting temperature averages according to measurement depth
        averages_by_depth = []
        for i in range(0, 6):
            average_item = []
            for month in averages_by_month:
                average_item.append(month[i])
            averages_by_depth.append(average_item)

        # Creating the line
        self.g_text = 'GROUND TEMPERATURES,' + str(len(ground_temperatures_depths)) + ','

        for index, depth in enumerate(ground_temperatures_depths):
            self.g_text += str(depth) + ','
            self.g_text += soil_conductivities[index] + ','
            self.g_text += soil_densities[index] + ','
            self.g_text += soil_specific_heats[index] + ','
            for average in averages_by_depth[index]:
                self.g_text += str(average) + ','

        # Stripping the last coma
        self.g_text = self.g_text[:-1]

    def create_blank_set(self):
        """
        Function creates data set in the EPW format with all values marked as missing (default values from self.fields
        variable).
        """
        year = self.converted_data[0][0][0][0:4]
        for i in range(0, 8760):
            line = [year, 0, 0, 0, 0]
            line[1] = str(int(self.converted_data[0][i][0][4:6]))  # month
            line[2] = str(int(self.converted_data[0][i][0][6:8]))  # day
            line[3] = str(int(self.converted_data[0][i][0][8:10]) + 1)  # hour
            line[4] = '60'  # minute

            for j in range(5, 35):
                line.append(self.fields[j][2])

            self.default_set.append(line)

    def fill_blank_set(self):
        """
        Function exchanges missing values in previously created data set with actual values, when available.
        """
        for index, item in enumerate(self.default_set):
            for field_num, field in enumerate(item):
                table_num = self.fields[field_num][6]
                column = self.fields[field_num][7]

                # If there exists a table and column where data is stored, value from default set is exchanged with
                # this value
                if table_num != 999:
                    self.default_set[index][field_num] = self.converted_data[table_num][index][column]

    def modify_flags(self):
        """
        Function that modifies flags of non-missing values. Flags are defined in self.fields variable according to
        Energy Plus manual.
        """
        for item in self.default_set:
            flag = ''
            for i in range(6, 35):
                # Checking if the value in the set has the default value for the field
                if item[i] != self.fields[i][2]:
                    flag += self.fields[i][4]
                else:
                    flag += self.fields[i][3]
                flag += self.fields[i][5]
            item[5] = flag

    def prepare_header(self):
        """
        Function that prepares heading lines in the .epw file.
        """
        cityname = Settings.cityname
        regionname = Settings.regionname
        countryname = Settings.country
        WMO = '123456'  # WMO station id - default value

        # calculating mean elevation
        # elev = 0
        # for station in self.station_list:
        #     elev += float(station[5])
        # elev = str(elev/8)

        elev = Settings.elevation

        # preparing text stating for which stations the weather data is collected
        c_text = 'Weather data obtained from following stations:'
        for station in Reporter.station_list:
            c_text += ' ' + station[0] + ': ' + station[8] + ' (' + station[9] + ') ID: ' + station[2] + ' |'

        header = []
        header.append(
            'LOCATION,' + cityname + ',' + regionname + ',' + countryname + ',DWD,' + WMO + ','
            + self.lat + ',' + self.lon + ',1.0,' + elev)
        header.append('DESIGN CONDITIONS,0')
        header.append('TYPICAL/EXTREME PERIODS,0')
        header.append(self.g_text)
        header.append('HOLIDAYS/DAYLIGHT SAVINGS,No,0,0,0')
        header.append('COMMENTS 1, Data set prepared by Weather Data Converter. ' + c_text)
        header.append('COMMENTS 2, Made at TU Dresden')
        header.append('DATA PERIODS,1,1,Data,Sunday,1/1,12/31')

        self.heading = header

    def write_epw_file(self):
        """
        Function that merges all prepared lines together in a .epw file and saves it in a defined place.
        """
        file = open(self.output_path, "w", encoding='utf-8')

        for line in self.heading:
            file.write(str(line) + '\n')

        for i in range(0, 8760):
            line = ''
            for item in self.default_set[i]:
                line += str(item) + ','
            line = line[:-1]
            file.write(line + '\n')

        file.close()

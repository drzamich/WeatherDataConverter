class DataOutputer:
    """
    This class, given the prepared sets of climate data, prepares the EPW file
    """

    def __init__(self,prepared_data,station_list):
        self.prepared_data = prepared_data
        self.station_list = station_list

        self.def_set = []

        self.fields = [
            #[field_number, field_name, default (missing)_value, flag_missing, flag_available, uncertainty,
            # data_set_table, table_column]
            [1, 'Year', '1980','','','',999,999],
            [2, 'Month', '1','','','',999,999],
            [3, 'Day','1','','','',999,999],
            [4, 'Hour','1','','','',999,999],
            [5, 'Minute','60','','','',999,999],
            [6, 'Data source and uncertainty flags','?0?0?0?0?0?0?0?0?0?0?0?0?0?0?0?0?0?0?0?0?0?0','','','',999,999],
            [7, 'Dry Bulb Temperature','99.9','?','A','7',0,3],
            [8, 'Dew Point Temperature', '99.9', '?', 'E', '7',0,4],
            [9, 'Relative humidity', '999', '?', 'A', '7',0,5],
            [10, 'Atmospheric Station Pressure', '999999', '?', 'A', '7',3,3],
            [11, 'Extraterrestrial Horizontal Radiation', '9999', '','','',999,999],
            [12, 'Extraterrestrial Direct Normal Radiation', '9999', '','','',999,999],
            [13, 'Horizontal Infrared Radiation Intensity','9999','?','E','0',5,9],
            [14, 'Global Horizontal Radiation', '9999','?','A','0',999,999],
            [15, 'Direct Normal Radiation','0','?','D','0',5,8],
            [16, 'Diffuse Horizontal Radiation','0','?','D','0',5,6],
            [17, 'Global Horizontal Illuminance','999999','?','A','0',999,999],
            [18, 'Direct Normal Illuminance','999999','?','A','0',999,999],
            [19, 'Diffuse Horizontal Illuminance','999999','?','A','0',999,999],
            [20, 'Zenith Luminance','9999','?','A','0',999,999],
            [21, 'Wind Direction','999','?','A','0',7,3],
            [22, 'Wind Speed','999','?','A','0',7,4],
            [23, 'Total Sky Cover','99','?','A','0',1,2],
            [24, 'Opaque Sky Cover','99','?','A','0',999,999],
            [25, 'Visibility','9999','?','A','0',999,999],
            [26, 'Ceiling Height','99999','?','A','0',999,999],
            [27, 'Present Weather Observation','9','','','',999,999],
            [28, 'Present Weather Codes','999999999','','','',999,999],
            [29, 'Precipitable Water','999','?','A','0',999,999],
            [30, 'Aerosol Optical Depth','.999','?','A','0',999,999],
            [31, 'Snow Depth','999','?','A','0',999,999],
            [32, 'Days Since Last Snowfall','99','?','A','0',999,999],
            [33, 'Albedo','','','','',999,999],
            [34, 'Liquid Precipitation Depth','','','','',999,999],
            [35, 'Liquid Precipitation Quantity','','','','',999,999]
        ]
        self.field_number = len(self.fields)
        self.prepare_data()

    def prepare_data(self):
        self.prepare_soil_data()
        self.create_blank_set()
        self.fill_blank_set()
        print(self.def_set)

    def prepare_soil_data(self):
        """
        This function creates the string with GROUND TEMPERATURES in the .epw file
        :return:
        """
        soil_temperatures = self.prepared_data[4]

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
                    if temp == -999:
                        continue
                    else:
                        count += 1
                        sum += temp

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

        year = self.prepared_data[0][0][0][0:4]
        for i in range (0,8760):
            line = [year,0,0,0,0]
            line[1] = str(int(self.prepared_data[0][i][0][4:6]))        #month
            line[2] = str(int(self.prepared_data[0][i][0][6:8]))        #day
            line[3] = str(int(self.prepared_data[0][i][0][8:10])+1)     #hour
            line[4] = '60'                                              #minute

            for j in range (5,35):
                line.append(self.fields[j][2])

            self.def_set.append(line)

    def fill_blank_set(self):
        for index,item in enumerate(self.def_set):
            for field_num, field in enumerate(item):
                table_num = self.fields[field_num][6]
                column = self.fields[field_num][7]

                if table_num != 999:
                    self.def_set[index][field_num] = self.prepared_data[table_num][index][column]


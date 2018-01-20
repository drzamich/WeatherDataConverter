import Settings
import math
import sys
import FileExplorer

observed_characteristics = Settings.observedCharacteristics

class StationSearcher(FileExplorer.FileExplorer):

    def __init__(self,year,latitude,longitude):
        self.year = year
        self.latitude = latitude
        self.longitude = longitude

        self.station_list = self.create_station_list(self.year,self.latitude,self.longitude)

    def create_station_list(self,year,latitude,longitude):
        station_list = []

        for char in observed_characteristics:
            char_name = char[0]
            char_short = char[1]

            zip_list = self.get_directory_listing(char_name,'.zip')

            #Getting characteristics file
            char_file_name = char_short.upper()+ '_Stundenwerte_Beschreibung_Stationen.txt'

            filepath = self.generate_dirpath(char_name) + char_file_name

            if not self.offline_data:
                self.download_file(char_name,char_file_name)
                filepath = self.generate_dirpath(type='download') + char_file_name

            char_file = self.get_txt_as_list(filepath)

            char_file_converted = self.convert_characteristics_file(char_file)
            combined_list = self.combine_zips_and_characteristics(char_file_converted,zip_list)
            best_station = self.choose_best_station(combined_list,self.year,latitude,longitude)
            best_station.insert(0,char_name)
            best_station.insert(1,char_short)
            station_list.append(best_station)
        return station_list


    #This function converts the raw txt file with station list to a python list
    def convert_characteristics_file(self,char_file):
        char_file_converted = []
        for i in range(2, len(char_file)):
            splitted = char_file[i].split()  # splitting the single line of the list
            # The line of the file has been splitted where empty spaces occur
            # Some stations however have empty spaces in their names
            # The following code deals with that problem
            if (len(splitted) > 8):
                override = len(splitted) - 8
                bundesland = splitted[len(splitted) - 1]

                #putting the name of the city together
                name = ''
                for j in range(0, override + 1):
                    if (j == 0):
                        name = name + splitted[6 + j]
                    else:
                        name = name + ' ' + splitted[6 + j]

                splitted[6] = name
                splitted[7] = bundesland

                for j in range(0, override):
                    del splitted[-1]
            char_file_converted.append(splitted)

        return char_file_converted


    #This function compares the station characteristics list with the zip file list
    #It happens that the station listed on the station list in txt file does not
    #Posses a file with data. This function checks if such data file exists and
    #Only leaves the stations for which a data file exists
    #Also it changes the end_date parameter to such value as in the data set defined
    #In the zip file name
    def combine_zips_and_characteristics(self,char_file,zip_files):
        combined_list = []
        for zip_file in zip_files:
            split = zip_file.split('_')
            id = split[2]

            #Special case for solar data - zip files do not have dates in names

            for station in char_file:
                if id == station[0]:
                    #Inserting dates from the zip filename to the station list
                    #Case for solar data is excluded
                    if str(split[3]) != 'row.zip':
                        station[1] = split[3]
                        station[2] = split[4]
                    combined_list.append(station)

        #Sorting the list according to the ID of the station
        combined_list.sort(key=lambda x: x[0])
        return combined_list

    def choose_best_station(self,station_list,year,lat,lon):
        startdate = int(str(year) + '0101')
        enddate = int(str(year)+'1231')
        distancemax = sys.maxsize

        for station in station_list:
            if int(station[1]) <= startdate and int(station[2]) >= enddate:
                distance = self.gpsdistance(lat,lon,float(station[4]),float(station[5]))
                if distance < distancemax:
                    beststation = station
                    distancemax = distance

        return beststation

    def gpsdistance(self, lat1, lon1, lat2, lon2):
        R = 6371000
        lat1 = math.radians(lat1)
        lat2 = math.radians(lat2)

        dlat = abs(lat1 - lat2)
        dlon = abs(lon1 - lon2)
        dlon = math.radians(dlon)

        a = (math.sin(0.5 * dlat)) ** 2 + math.cos(lat1) * math.cos(lat2) * (math.sin(0.5 * dlon)) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c
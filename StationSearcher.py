import Settings
import math
import sys
import FileExplorer

observed_characteristics = Settings.observedCharacteristics

class StationSearcher(FileExplorer.FileExplorer):
    """
    This class is reponsible, given the year and coordinates (longitude and latitude), to provide a list of
    stations for which it is most favourable to extract weather data for.
    """

    def __init__(self,year,latitude,longitude):
        """
        :param year: year for which the weather data is needed
        :param latitude: latitude of the location in degrees
        :param longitude: longitude of the location in degrees
        """
        self.year = year
        self.latitude = latitude
        self.longitude = longitude

        self.station_list = []
        self.create_station_list()

    def create_station_list(self):
        """
        Function responsible for creating a list of most favourable stations.
        A station is chosen for each climate element based on it's distance from the set location
        :return:
        """
        for char in observed_characteristics:
            char_name = char[0]
            char_short = char[1]

            #Creating list of .zip files (files containing weather data)
            zip_list = self.get_directory_listing(char_name,'.zip')

            #Getting stations characteristics file
            #Defining filename
            char_file_name = char_short.upper()+ '_Stundenwerte_Beschreibung_Stationen.txt'

            #Defining filepath
            filepath = self.generate_dirpath(char_name) + char_file_name

            #Downloading characteristics file if neccessary
            if not self.offline_data:
                self.download_file(char_name,char_file_name)
                filepath = self.generate_dirpath(type='download') + char_file_name

            #Saving characteristic file to a list
            char_file = self.get_txt_as_list(filepath)

            #Converting the characteristics file to format suitable for further analisys
            char_file = self.convert_characteristics_file(char_file)

            #Combining the list of the stations from the characteristic file with the .zip files list
            #In the process stations for which there are no .zip files with weather data available are removed from
            #The list
            combined_list = self.combine_zips_and_characteristics(char_file,zip_list)

            #Choosing station from the list that is closest to the given location
            best_station = self.choose_best_station(combined_list)

            #In the first and second column of the list with best stations, inserting information about climate element
            best_station.insert(0,char_name)
            best_station.insert(1,char_short)

            #Adding station information to the final stations lisrt
            self.station_list.append(best_station)

    #This function converts the raw txt file with station list to a python list
    def convert_characteristics_file(self,char_file):
        """
        Function responsible for converting the file with stations characteristics
        :param char_file: raw content of the stations list file
        :return: list with stations characteristics sorted nicely in a python format
        """
        char_file_converted = []
        for i in range(2, len(char_file)):
            splitted = char_file[i].split()  # splitting the single line of the list
            # The line of the file has been splitted where empty spaces occur
            # Some stations however have empty spaces in their names (for names that are longer than one word)
            # The following code deals with that problem
            if (len(splitted) > 8):   #if the line has more than 8 elements, that means the name of city is longer than
                                      #one word
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

                #deleting unneccessary columns
                for j in range(0, override):
                    del splitted[-1]

            #Adding the line to the final list
            char_file_converted.append(splitted)

        return char_file_converted

    def combine_zips_and_characteristics(self,char_file,zip_files):
        """
        Function responsible for checking if the station from the stations list has a corresponding zip file
        with weather data. It also inserts the dates marking beggining and end of station operation coded in the
        zip filename
        :param char_file: stations list for appropriate climate element
        :param zip_files: list of .zip files for an appropriate element
        :return: stations list with removed entries for which weather data file does not exist
        """
        combined_list = []
        for zip_file in zip_files:
            #Naming convention of the zip files is that elements of the name are separated with the '_'
            split = zip_file.split('_')
            id = split[2]  #ID of the staion is always the third element of the name

            #Checking looking for staion with same ID on the stations list
            for station in char_file:
                if id == station[0]:   #if the IDs are the same, saving the station to the final list
                    #Inserting dates from the zip filename to the station list
                    #Case for solar data is excluded as those files don't have dates hidden in zip filenames
                    if str(split[3]) != 'row.zip':
                        station[1] = split[3]
                        station[2] = split[4]
                    combined_list.append(station)

        #Sorting the list according to the ID of the station
        combined_list.sort(key=lambda x: x[0])
        return combined_list

    def choose_best_station(self,station_list):
        """
        Function repsponsible for, based on the year and coordinates, choosing the most favourable station from the
        stations list. Based on the Haversine formula it calculates the distance from the given location to every
        station and then chooses the staion with minimum distance if there exists weather data for this station in the
        given year.

        :param station_list: stations list
        :return: characteristics of the most favourable station saved in a list
        """
        startdate = int(str(self.year) + '0101')
        enddate = int(str(self.year)+'1231')
        distancemax = sys.maxsize

        for station in station_list:
            #Checking if the given year is within the opration range of the station
            if int(station[1]) <= startdate and int(station[2]) >= enddate:
                #Calculating the distance from the station to the given coordinates
                distance = self.gpsdistance(self.latitude,self.longitude,float(station[4]),float(station[5]))
                if distance < distancemax:
                    beststation = station
                    distancemax = distance

        #Returning most favourable station's characteristics
        return beststation

    def gpsdistance(self, lat1, lon1, lat2, lon2):
        """
        Function responsible for calculating, using the Haversine formula, distance in meters from two points on Earth
        based on their coordinates.
        :param lat1: latitude of the 1st point in degrees
        :param lon1: longitude of the 1st point in degrees
        :param lat2: latitude of the 2nd point in degrees
        :param lon2: longitude of the 2nd point in degrees
        :return:
        """
        R = 6371000 #Earth's radius in meters
        lat1 = math.radians(lat1)
        lat2 = math.radians(lat2)

        dlat = abs(lat1 - lat2)
        dlon = abs(lon1 - lon2)
        dlon = math.radians(dlon)

        a = (math.sin(0.5 * dlat)) ** 2 + math.cos(lat1) * math.cos(lat2) * (math.sin(0.5 * dlon)) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c
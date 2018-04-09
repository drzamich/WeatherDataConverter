import math
import os
from pathlib import Path
import pickle
import sys

import FileExplorer
import Reporter
import Settings


class StationSearcher(FileExplorer.FileExplorer):
    """
    This class is responsible, given the year and coordinates (longitude and latitude), to provide a list of
    stations for which it is most favourable to extract weather data for.
    """

    def __init__(self):
        Reporter.set_status('Searching for stations', 1)

        self.year = Settings.year
        self.latitude = Settings.lat
        self.longitude = Settings.lon

        self.station_list = []

        # Load list of stations that are excluded from searching
        self.load_forbidden_list()

        # Create most favourable station list
        self.create_station_list()

        # If after creating station list, it is not complete, error is raised to the user
        if not Reporter.complete_station_list:
            Reporter.set_status('ERROR: Not possible to find stations for given input parameters.', 0)

        Reporter.station_list = self.station_list

    def create_station_list(self):
        """
        Function responsible for creating a list of most favourable stations.
        A station is chosen for each climate element based on it's distance from the set location
        """
        for char in Settings.observedCharacteristics:
            char_name = char[0]
            char_short = char[1]

            # Creating list of .zip files (files containing weather data)
            zip_list = self.get_directory_listing(char_name, '.zip')

            # Getting stations characteristics file
            # defining filename
            char_file_name = char_short.upper() + '_Stundenwerte_Beschreibung_Stationen.txt'

            # Defining file path
            filepath = self.generate_dirpath(char_name) + char_file_name

            # Downloading characteristics file if necessary
            if not Settings.use_offline_data:
                self.download_file(char_name, char_file_name)
                filepath = self.generate_dirpath(type='download') + char_file_name

            # Saving characteristic file to a list
            char_file = self.get_txt_as_list(filepath)

            # Converting the characteristics file to format suitable for further analysis
            char_file = self.convert_characteristics_file(char_file)

            # Combining the list of the stations from the characteristic file with the .zip files list
            # in the process stations for which there are no .zip files with weather data available are removed from
            # the list
            combined_list = self.combine_zips_and_characteristics(char_file, zip_list)

            # Removing from the list stations that are on the forbidden list
            cleared_list = self.remove_forbidden(combined_list, char_name)

            # Choosing station from the list that is closest to the given location
            best_station, best_station_exists = self.choose_best_station(cleared_list)

            # If it was not possible to find any station for the current year and location,
            # the completion flag is set to False
            if not best_station_exists:
                Reporter.complete_station_list = False

            # In the first and second column of the list with best stations, inserting information about climate element
            best_station.insert(0, char_name)
            best_station.insert(1, char_short)

            # Adding station information to the final stations list
            self.station_list.append(best_station)

    def convert_characteristics_file(self, char_file):
        """
        Function responsible for converting the file with stations characteristics from txt to Python list object
        :param char_file: raw content of the stations list file
        :return: list with stations characteristics sorted nicely in a python format
        """
        char_file_converted = []
        for i in range(2, len(char_file)):
            split_line = char_file[i].split()  # splitting the single line of the list
            # The line of the file has been split where empty spaces occur
            # Some stations however have empty spaces in their names (for names that are longer than one word)
            # The following code deals with that problem
            if len(split_line) > 8:  # if the line has more than 8 elements, that means the name of city is longer than
                # one word
                override = len(split_line) - 8
                bundesland = split_line[len(split_line) - 1]

                # putting the name of the city together
                name = ''
                for j in range(0, override + 1):
                    if j == 0:
                        name = name + split_line[6 + j]
                    else:
                        name = name + ' ' + split_line[6 + j]

                split_line[6] = name
                split_line[7] = bundesland

                # deleting unnecessary columns
                for j in range(0, override):
                    del split_line[-1]

            # Adding the line to the final list
            char_file_converted.append(split_line)

        return char_file_converted

    def combine_zips_and_characteristics(self, char_file, zip_files):
        """
        Function responsible for checking if the station from the stations list has a corresponding zip file
        with weather data. It also inserts the dates marking beginning and end of station operation coded in the
        zip filename
        :param char_file: stations list for appropriate climate element
        :param zip_files: list of .zip files for an appropriate element
        :return: stations list with removed entries for which weather data file does not exist
        """
        combined_list = []
        for zip_file in zip_files:
            # Naming convention of the zip files is that elements of the name are separated with the '_'
            split = zip_file.split('_')
            id = split[2]  # ID of the station is always the third element of the name

            # Checking looking for station with same ID on the stations list
            for station in char_file:
                if id == station[0]:  # if the IDs are the same, saving the station to the final list
                    # Inserting dates from the zip filename to the station list
                    # Case for solar data is excluded as those files don't have dates hidden in zip file names
                    if str(split[3]) != 'row.zip':
                        station[1] = split[3]
                        station[2] = split[4]
                    combined_list.append(station)

        # Sorting the list according to the ID of the station
        combined_list.sort(key=lambda x: x[0])
        return combined_list

    def choose_best_station(self, station_list):
        """
        Function responsible for, based on the year and coordinates, choosing the most favourable station from the
        stations list. Based on the Haversine formula it calculates the distance from the given location to every
        station and then chooses the station with minimum distance if there exists weather data for this station in the
        given year.

        :param station_list: stations list
        :return: characteristics of the most favourable station saved in a list
        """
        startdate = int(str(self.year) + '0101')
        enddate = int(str(self.year) + '1231')
        distancemax = sys.maxsize
        beststation = []
        best_station_exists = False

        for station in station_list:
            # Checking if the given year is within the operation range of the station
            if int(station[1]) <= startdate and int(station[2]) >= enddate:
                # Calculating the distance from the station to the given coordinates
                distance = self.gpsdistance(self.latitude, self.longitude, float(station[4]), float(station[5]))
                if distance < distancemax:
                    beststation = station
                    distancemax = distance
                    best_station_exists = True

        # Returning most favourable station's characteristics and existence flag
        return beststation, best_station_exists

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
        R = 6371000  # Earth's radius in meters
        lat1 = math.radians(lat1)
        lat2 = math.radians(lat2)

        dlat = abs(lat1 - lat2)
        dlon = abs(lon1 - lon2)
        dlon = math.radians(dlon)

        a = (math.sin(0.5 * dlat)) ** 2 + math.cos(lat1) * math.cos(lat2) * (math.sin(0.5 * dlon)) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def load_forbidden_list1(self):
        """
        Function loads list of forbidden stations saved as a serialized object
        """
        path = Settings.dirpath_program + os.sep + 'programdata' + os.sep + 'forbidden_stations.pickle'

        if not Path(path).is_file():  # There is no forbidden list yet
            self.forbidden_list = []
        else:
            pickle_in = open(path, 'rb')
            self.forbidden_list = pickle.load(pickle_in)
            pickle_in.close()

    def load_forbidden_list(self):
        self.forbidden_list = []
        path = Settings.dirpath_program + os.sep + 'programdata' + os.sep + 'forbidden_stations.txt'

        try:
            file_list = self.get_txt_as_list(path)
        except FileNotFoundError:
            return

        for line in file_list:
            line_split = line.split('\t')

            year = line_split[0]
            station_id = line_split[1]
            char_name = line_split[2].rstrip()
            item = [year, station_id, char_name]

            self.forbidden_list.append(item)


    def remove_forbidden(self, station_list, char_name):
        """
        Function removes stations listed on the forbidden list from the list of stations that are later
        used for choosing most favorable station.
        :param station_list: list of the stations for a specific climate characteristic
        :param char_name: name of the climate characteristics
        :return: station list with without forbidden stations
        """
        cleared_list = []
        for station in station_list:
            station_id = station[0]
            forbidden = False
            for forbidden_station in self.forbidden_list:
                forbidden_year = forbidden_station[0]
                forbidden_id = forbidden_station[1]
                forbidden_char_name = forbidden_station[2]
                if (forbidden_year == str(self.year) or forbidden_year == 'all') \
                        and forbidden_id == station_id \
                        and (forbidden_char_name == char_name or forbidden_char_name == 'all'):
                    forbidden = True
                    break
            if not forbidden:
                cleared_list.append(station)

        return cleared_list

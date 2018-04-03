import os
from pathlib import Path
import pickle

import FileExplorer
import Reporter
import Settings
import StationSearcher


class DataReader(FileExplorer.FileExplorer):
    """
    This class is responsible for searching directories with weather data,
    looking for and opening proper zip files with weather data txt files inside,
    reading the txt files and preliminary conversion of weather data
    """

    def __init__(self):
        print('DataReader')
        Reporter.setStatus('Reading data',11)
        self.year = Settings.year
        self.station_list = Reporter.station_list
        self.corrupted_data = True

        # The program tries to generate a valid data set until the data is not marked as corrupted,
        # which occurs when data set from the station does not have enough number of records for a year
        # defined by Settings.min_rec
        while self.corrupted_data:
            self.extracted_data = []
            self.corrupted_data = False
            self.generate_raw_set()

        Reporter.extracted_data = self.extracted_data

        Reporter.setStatus('Data read', 20)

    def generate_raw_set(self):
        """
        :return: set of 7 lists containing raw data extracted from the txt files from weather stations
                 this set is saved in the raw_data_set variable
        """
        for index, station in enumerate(self.station_list):
            raw_data = self.get_raw_data(station)
            raw_data = self.strip_other_years(self.year, raw_data)

            # If the amount of data for specific climate element and year is insufficient
            # Data set is marked as empty and station is added to the forbidden station list
            if len(raw_data) < Settings.min_rec:
                print("-Insufficient number of records for " + station[0])
                self.corrupted_data = True
                self.forbid_station(self.year, station[0], station[2])

                # After adding station to the forbidden list, a new station list is created
                searcher = StationSearcher.StationSearcher()
                self.station_list = searcher.station_list
                Reporter.setStatus('Reading data', 11)

                return  # Jump back to the calling function to repeat the process from the start

            raw_data = self.delete_columns(raw_data, index)

            self.extracted_data.append(raw_data)

    def get_raw_data(self, station):
        """
        :param station: list containing characteristics of the station for which the data needs to be extracted
        :return: list containing content of produkt_*.txt file
        """
        char_name = station[0]
        char_short = station[1]
        id = station[2]
        startdate = station[3]
        enddate = station[4]

        # Based on the station details, generating name of the .zip file with weather data
        filename = 'stundenwerte_'+char_short.upper()+'_'+id+'_'+startdate+'_'+enddate+'_hist.zip'

        # Solar data has different naming convention, hence the exception
        if char_name == 'solar':
            filename = 'stundenwerte_' + char_short.upper() + '_' + id + '_row.zip'

        # Generating path to the file
        path = self.generate_dirpath(char_name)+filename

        # If no offline data is used, downloading the zip fiile
        if not Settings.use_offline_data:
            self.download_file(char_name,filename)
            path = self.generate_dirpath(type='download')+filename

        # Getting contents of the produkt*.txt file inside the zip file
        if not Settings.testing_mode:
            return self.get_txt_from_zip(path,file_prefix='produkt')
        else:
            # If the testing_mode is on, getting the data from files in the testing/directory
            return self.get_txt_as_list('data/testing/'+char_name+'.txt')

    def strip_other_years(self,year,data_list):
        """
        :param year: the year for which the weather data has to be extracted
        :param data_list: raw data list
        :return: raw data list without entries that aren't from the defined year
        """
        new_list = []
        for line in data_list:
            # splitting each line of the file where the semicolon is. also decoding the file from bytes to utf8 format
            # for some reason it is only necessary when the text file is loaded from the zip file
            if not Settings.testing_mode:  # in the testing mode I use pure txt files (not packed in zip) -
                                           # no decoding needed
                line_split = line.decode('utf8').split(";")
            else:
                line_split = line.split(";")
            date = line_split[1]

            # If the date starts with the given year, saving the whole line in the new list
            if date.startswith(str(year)):
                newline = []
                for part in line_split:
                    newline.append(part)
                newline[1] = date[0:10]  # YYYYmmddHH - only saving the first 10 digits of the date - sometimes the time
                                         # stamp also contains minutes, that are not necessary

                new_list.append(newline)

        return new_list

    def delete_columns(self,data_list,char_index):
        """
        :param data_list: raw data list
        :param char_index: index (position number in the observedCharacteristics variable) of the climate element
        :return: data list without columns that are not listed in the observedCharacteristics variable
                    for the given climate element
        """
        new_list = []
        for line in data_list:
            new_list_item = []
            date = line[1]
            new_list_item.append(date)
            # Reference to the list of columns in the Settings module
            columns_list = Settings.observedCharacteristics[char_index][2]
            for column in columns_list:
                new_list_item.append(line[column].strip())
            new_list.append(new_list_item)

        return new_list

    def forbid_station(self, year, char_name, station_id):
        """
        When the number of records for a given year is not sufficient, another station has to be chosen to
        provide data for a certain climate element. Station with insufficient data is added to the forbidden list
        to avoid using it in the future for the specific year and climate element
        """
        forbidden_item = [year,char_name,station_id]
        path = 'programdata'+os.sep+'forbidden_stations.pickle'

        if not Path(path).is_file():
            forbidden_list = [forbidden_item]  # There is no forbidden list yet
        else:
            pickle_in = open(path,'rb')
            forbidden_list = pickle.load(pickle_in)
            forbidden_list.append(forbidden_item)
            pickle_in.close()

        pickle_out = open(path,'wb')
        pickle.dump(forbidden_list, pickle_out)
        pickle_out.close()



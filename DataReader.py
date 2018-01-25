import Settings
import FileExplorer

observed_characteristics = Settings.observedCharacteristics
dirpath_local = Settings.dirpath_offline
dirpath_ftp = Settings.dirpath_ftp
dirpath_downloaded = Settings.dirpath_downloaded
offline_data = Settings.use_offline_data

class DataReader(FileExplorer.FileExplorer):
    """
    This class is responsible for searching directories with weather data,
    looking for and opening proper zip files with weather data txt files inside,
    reading the txt files and preliminary conversion of weather data
    """

    def __init__(self,year,station_list):
        """
        :param year: the year for which the weather data has to be extracted
        :param station_list: list of stations created in the StationSearcher class, containing station information
                             needed for extraction of weather data
        """
        self.year = year
        self.station_list = station_list
        self.raw_data_set = []
        self.generate_raw_set()

    def generate_raw_set(self):
        """
        :return: set of 7 lists containing raw data extracted from the txt files from weather stations
                 this set is saved in the raw_data_set variable
        """
        for index,station in enumerate(self.station_list):
            raw_data = self.get_raw_data(station)
            raw_data = self.strip_other_years(self.year,raw_data)
            raw_data = self.delete_columns(raw_data,index)
            self.raw_data_set.append(raw_data)

    def get_raw_data(self,station):
        """
        :param station: list containing characteristics of the station for which the data needs to be extracted
        :return: list containing content of produkt_*.txt file
        """
        char_name = station[0]
        char_short = station[1]
        id = station [2]
        startdate = station[3]
        enddate = station[4]

        #Based on the station details, generating name of the .zip file with weather data
        filename = 'stundenwerte_'+char_short.upper()+'_'+id+'_'+startdate+'_'+enddate+'_hist.zip'

        #Solar data has different naming convention, hence the exception
        if char_name == 'solar':
            filename = 'stundenwerte_' + char_short.upper() + '_' + id + '_row.zip'

        #Generating path to the file
        path = self.generate_dirpath(char_name)+filename

        #If no offline data is used, downloading the zip fiile
        if not offline_data:
            self.download_file(char_name,filename)
            path = self.generate_dirpath(type='download')+filename

        #Getting contents of the produkt*.txt file inside the zip file
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
            if not Settings.testing_mode:  # in the testing mode I use pure txt files (not packed in zip) - no decoding needed
                line_splitted = line.decode('utf8').split(";")
            else:
                line_splitted = line.split(";")
            date = line_splitted[1]

            #If the date starts with the given year, saving the whole line in the new list
            if date.startswith(str(year)):
                newline = []
                for part in line_splitted:
                    newline.append(part)
                newline[1] = date[0:10]  #YYYYmmddHH - only saving the first 10 digits of the date, as sometimes the time
                                         #stamp also contains minutes, that are not neccessary

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
            #Reference to the list of columns in the Settings module
            columns_list = Settings.observedCharacteristics[char_index][2]
            for column in columns_list:
                new_list_item.append(line[column].strip())
            new_list.append(new_list_item)

        return new_list





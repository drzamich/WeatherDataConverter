import Settings
import FileExplorer

observed_characteristics = Settings.observedCharacteristics
dirpath_local = Settings.dirpath_offline
dirpath_ftp = Settings.dirpath_ftp
dirpath_downloaded = Settings.dirpath_downloaded
offline_data = Settings.use_offline_data

class DataReader(FileExplorer.FileExplorer):

    def __init__(self,year,station_list):
        self.year = year
        self.station_list = station_list
        self.raw_data_set = self.generate_raw_set()

    def generate_raw_set(self):
        raw_data_set = []
        for index,station in enumerate(self.station_list):
            raw_data = self.get_raw_data(station)
            raw_data = self.strip_other_years(self.year,raw_data)
            raw_data = self.delete_columns(raw_data,index)
            raw_data_set.append(raw_data)
        return raw_data_set

    def get_raw_data(self,station):
        char_name = station[0]
        char_short = station[1]
        id = station [2]
        startdate = station[3]
        enddate = station[4]

        filename = 'stundenwerte_'+char_short.upper()+'_'+id+'_'+startdate+'_'+enddate+'_hist.zip'

        if char_name == 'solar':
            filename = 'stundenwerte_' + char_short.upper() + '_' + id + '_row.zip'

        path = self.generate_dirpath(char_name)+filename

        if not offline_data:
            self.download_file(char_name,filename)
            path = self.generate_dirpath(type='download')+filename

        if Settings.testing_mode:
            return self.get_txt_as_list('data/testing/'+char_name+'.txt')
        else:
            return self.get_txt_from_zip(path)

    def strip_other_years(self,year,data_list):
        new_list = []
        for line in data_list:
            # splitting each line of the file where the semicolon is. also decoding the file from bytes to utf8 format
            # for some reason it is only necessary when the text file is loaded from the zip file

            if not Settings.testing_mode:  # in the testing mode I use pure txt files (not packed in zip) - no decoding needed
                line_splitted = line.decode('utf8').split(";")
            else:
                line_splitted = line.split(";")
            date = line_splitted[1]

            if date.startswith(str(year)):
                newline = []
                for part in line_splitted:
                    newline.append(part)
                newline[1] = date[0:10]  #YYYYmmddHH

                new_list.append(newline)

        return new_list

    def delete_columns(self,data_list,char_index):
        new_list = []
        for line in data_list:
            new_list_item = []
            date = line[1]
            new_list_item.append(date)
            for index in Settings.observedCharacteristics[char_index][2]:
                new_list_item.append(line[index].strip())

            new_list.append(new_list_item)

        return new_list





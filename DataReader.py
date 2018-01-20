import os
import ftplib
import Settings
import math
import sys
from pathlib import Path
import FileExplorer

observed_characteristics = Settings.observedCharacteristics
dirpath_local = Settings.dirpath_offline
dirpath_ftp = Settings.dirpath_ftp
dirpath_downloaded = Settings.dirpath_downloaded
offline_data = Settings.use_offline_data

class DataReader(FileExplorer.FileExplorer):

    def __init__(self,station_list):
        for station in station_list:
            raw_data = self.get_raw_data(station)
            print(raw_data)
            break

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

        return self.get_txt_from_zip(path)



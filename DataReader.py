import os
import ftplib
import Settings
import math
import sys
from pathlib import Path

observed_characteristics = Settings.observedCharacteristics
dirpath_local = Settings.dirpath_offline
dirpath_ftp = Settings.dirpath_ftp
dirpath_downloaded = Settings.dirpath_downloaded
offline_data = Settings.use_offline_data

class DataReader:

    def __init__(self,station_list):
        pass

    def get__data_file(self,station_id):
    def download_data_from_server(self,station_list):

        # This function downloads data from server in one go based on the staions IDs
        # It only needs to connect to the server once, therefore it limits queries send to server that may leed to issues
        # Like blocking the user

        # Connecting to the server
        try:
            ftp = ftplib.FTP('ftp-cdc.dwd.de')
            ftp.login(user='anonymous', passwd='')
        except Exception:
            print('Unable to connect to FTP server')

        for index, char in enumerate(observed_characteristics):

            char_name = char[0]
            char_short = char[1]

            if index != 5:
                path = dirpath_ftp + char_name + '/historical/'

            ftp.cwd(path)  # changing the directory
            ls = []
            ftp.retrlines('MLSD', ls.append)  # listing files in the directory

            station_id = station_list[index][1]
            filename_begin = 'stundenwerte_' + char_short.upper() + '_' + station_id

            # looking for the file that's name begins with our defined string
            for line in ls:
                line_splitted = line.split(";")
                for line_inner in line_splitted:
                    if str(line_inner).strip().startswith(filename_begin):
                        filename = str(line_inner).strip()

            # checking if our file already exists in the download folder
            filepath = dirpath_downloaded + '/' + char_name + '/' + filename
            if Path(filepath).is_file():
                continue

            # If the file does not exist, download process proceeds
            else:
                file = open(filepath, 'wb')
                try:
                    ftp.retrbinary('RETR %s' % filename, file.write)
                except Exception:
                    print('Unable to download file from FTP server')

                file.close()

        ftp.quit()
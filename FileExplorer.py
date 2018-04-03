import ftplib
import os
from pathlib import Path
import zipfile

import Settings


class FileExplorer:
    """
    This class contains functions are are helpful for other classes in managing files and directories
    """

    def get_directory_listing(self,char_name,*extensions):
        """
        :param char_name: name of the climate element
        :param extensions: unsorted list of extensions that the user wants to include on the file lsit
        :return: list of files with *extensions inside the hourly/historical/ folder for climate element
                given in char_name
        """
        files_list = []

        # Based on the climate element name, generating path to the directory
        path = self.generate_dirpath(char_name)

        if Settings.use_offline_data:
            files_list = os.listdir(path)

        else:
            # Using data from ftp server
            # Establishing FTP Connection
            try:
                ftp = ftplib.FTP(Settings.ftp_adress)
                ftp.login(user=Settings.ftp_user, passwd=Settings.ftp_pass)
            except Exception:
                print('Unable to connect to FTP server.')

            ftp.cwd(path)
            ls = []
            ftp.retrlines('MLSD', ls.append)  # listing files in the directory
            for line in ls:
                # Directory listing from ftp server contains many information separated with ";"
                # Therefore splitting lines is necessary
                line_splitted = line.split(';')
                for item in line_splitted:
                    for ext in extensions:
                        if ext in item:
                            files_list.append(item.strip())

            # Closing FTP connection
            ftp.close()

        return files_list

    def get_txt_from_zip(self, zip_filepath, file_prefix='produkt'):
        """
        :param zip_filepath: path to the zip file
        :param file_prefix: prefix of the txt file inside the zip file that is to be extracted
        :return: contents of the txt file as list
        """
        zf = zipfile.ZipFile(zip_filepath)

        # looking for txt file which name starts with file_prefix
        inside_zip = zf.namelist()
        for item in inside_zip:
            if str(item).startswith(file_prefix):
                file_data_name = str(item)

        file_data = zf.open(file_data_name)
        zf.close()

        # Returning the contents of txt file as a list
        return file_data.readlines()

    def download_file(self, char_name, filename):
        """
        :param char_name: name of the climate element
        :param filename: name of the file that will be downloaded
        :return: function downloads a file from FTP server and saves it in the data/download folder
        """
        dirpath_downloaded = Settings.dirpath_downloaded
        path_downloaded = dirpath_downloaded+filename  # path to the downloaded file

        # Downloading the file only if the file wasn't downloaded before
        if not Path(path_downloaded).is_file():
            dirpath_ftp = self.generate_dirpath(char_name)

            try:
                ftp = ftplib.FTP(Settings.ftp_adress)
                ftp.login(user=Settings.ftp_user, passwd=Settings.ftp_pass)
                ftp.cwd(dirpath_ftp)
            except Exception:
                print('Unable to connect to FTP server')

            try:
                file = open(path_downloaded,'wb')
                ftp.retrbinary('RETR %s' % filename, file.write)
                file.close
            except Exception:
                print('Unable to download file from FTP server')

            ftp.close()

    def get_txt_as_list(self, filepath):
        """
        :param filepath: path to the txt file
        :return: contents of the txt file as a list
        """
        file = open(filepath,'r')
        file_list = file.readlines()
        file.close()
        return file_list

    def generate_dirpath(self, char_name='air_temperature', type='repository'):
        """
        :param char_name: name of the climate element. default = air_temperature
        :param type: type of the generated dirpath
                        - repository: dirpath to the folder contains all the data files on local drive or FTP
                        - download: dirpath to the folder containing downloaded files
        :return: path to the folder
        """
        dirpath_local = Settings.dirpath_offline
        dirpath_ftp = Settings.ftp_dirpath
        dirpath_downloaded = Settings.dirpath_downloaded

        if type == 'repository':
            if Settings.use_offline_data:
                dirpath = dirpath_local
            else:
                dirpath = dirpath_ftp

            # Exception for solar data
            if char_name != 'solar':
                path = dirpath + char_name + os.sep + 'historical' + os.sep
            else:
                path = dirpath + char_name + os.sep

        elif type == 'download':
            path = dirpath_downloaded

        return path

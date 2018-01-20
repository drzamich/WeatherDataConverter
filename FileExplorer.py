import Settings
import ftplib
import os
from pathlib import Path
import zipfile

dirpath_downloaded = Settings.dirpath_downloaded

class FileExplorer:
    offline_data = Settings.use_offline_data

    def get_directory_listing(self,char_name,*extensions):
        files_list = []

        path = self.generate_dirpath(char_name)

        if self.offline_data:
            files_list = os.listdir(path)

        else:
            #using data from ftp server
            #Establishing FTP Connection
            try:
                ftp = ftplib.FTP('ftp-cdc.dwd.de')
                ftp.login(user='anonymous', passwd='')
            except Exception:
                print('Unable to connect to FTP server')

            ftp.cwd(path)
            ls = []
            ftp.retrlines('MLSD', ls.append)  # listing files in the directory
            for line in ls:
                line_splitted = line.split(';')
                for item in line_splitted:
                    for ext in extensions:
                        if ext in item:
                            files_list.append(item.strip())

            # closing FTP connection
            ftp.close()

        return files_list

    def get_txt_from_zip(self,zip_filepath,file_prefix='produkt'):
        zf = zipfile.ZipFile(zip_filepath)

        # looking for txt file which name starts with file_prefix
        inside_zip = zf.namelist()
        for item in inside_zip:
            if str(item).startswith(file_prefix):
                file_data_name = str(item)

        file_data = zf.open(file_data_name)
        zf.close()

        return file_data.readlines()

    def download_file(self,char_name,filename):
        dirpath_downloaded = Settings.dirpath_downloaded
        path_downloaded = dirpath_downloaded+'/'+filename

        #Downloading the fily only if the file wasn't downloaded before
        if not Path(path_downloaded).is_file():
            dirpath_ftp = self.generate_dirpath(char_name)

            try:
                ftp = ftplib.FTP('ftp-cdc.dwd.de')
                ftp.login(user='anonymous', passwd='')
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

    def get_txt_as_list(self,filepath):
        file = open(filepath,'r')
        file_list = file.readlines()
        file.close()
        return file_list

    def generate_dirpath(self, char_name='air_temperature', type='repository'):
        dirpath_local = Settings.dirpath_offline
        dirpath_ftp = Settings.dirpath_ftp
        dirpath_downloaded = Settings.dirpath_downloaded

        if type == 'repository':
            if self.offline_data:
                dirpath = dirpath_local
            else:
                dirpath = dirpath_ftp

            if char_name != 'solar':
                path = dirpath + char_name + '/historical/'
            else:
                path = dirpath + char_name + '/'

        elif type == 'download':
            path = dirpath_downloaded

        return path

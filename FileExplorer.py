import Settings
import ftplib
import os

offline_data = Settings.use_offline_data
dirpath_downloaded = Settings.dirpath_downloaded

class FileExplorer:


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

    def get_txt_from_zip(self):
        pass

    def get_txt_as_list(self,filepath):
        file = open(filepath,'r')
        file_list = file.readlines()
        file.close()
        return file_list

    def generate_dirpath(self, char_name):
        dirpath_local = Settings.dirpath_offline
        dirpath_ftp = Settings.dirpath_ftp


        if offline_data:
            dirpath = dirpath_local
        else:
            dirpath = dirpath_ftp

        if char_name != 'solar':
            path = dirpath + char_name + '/historical/'
        else:
            path = dirpath + char_name + '/'

        return path

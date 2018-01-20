'''
This class is responsible for searching directories either on local machine or on FTP Server
It is necessary to get informations about available data sets
'''

import Settings
import ftplib
import os

class DirectoryExplorer:


    #This function gives us the list of files with given extension in the directory
    #Either on local maschine or FTP Server
    def get_files_list(self,path,extension):

        files_list = []

        if self.offline_data:
            dirpath = self.dirpath_local
            pass

        else:
            dirpath = self.dirpath_ftp
            #using data from ftp server
            #Establishing FTP Connection
            try:
                ftp = ftplib.FTP('ftp-cdc.dwd.de')
                ftp.login(user='anonymous', passwd='')
            except Exception:
                print('Unable to connect to FTP server')

        if char_name != 'solar':
            path = dirpath + char_name + '/historical/'
        else:
            path = dirpath + char_name

        if self.offline_data:
            files_list = os.listdir(path)

        else:
            ftp.cwd(path)
            ls = []
            ftp.retrlines('MLSD', ls.append)  # listing files in the directory
            for line in ls:
                line_splitted = line.split(';')
                for item in line_splitted:
                    if extension in item:
                        files_list.append(item.strip())
            #closing FTP connection
            ftp.close()

        print(files_list)
        return files_list


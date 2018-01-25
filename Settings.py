"""
Variable defining if the program can use weather data previously downloaded from the FTP server
and stored on the local drive. If the value is set to 0, when searching for weather data, program will
connect to the DWD FTP server and download files from there. Therefore internet connection is required.

If the value is set to 1, program will search directory defined in dirpath_offline in search for weather data
The folder hierarchy there must be the same as on the FTP Server
"""
use_offline_data = 1
dirpath_offline = 'E:\\DOKUMENTY\\WeatherData\\'

"""
Variable storing path to the directory with hourly climate data on the FTP server
"""
dirpath_ftp = '/pub/CDC/observations_germany/climate/hourly/'

"""
Variable controlling if the testing mode is on. If it's off, the program generates data basing on the year and 
coordinates using stored in an appropriate place on local drive or FTP server.
If it's on, then the program uses data from txt files stored in data/testing directory
"""
testing_mode = 1


"""
Variable storing information about weather climate elements, based on the design of folders, filenames and 
files containing weather data.

1st column contains name of the climate element. It corresponds to names of folders in climate/hourly/ directory

2nd column contains letters that server as a shortcut of the name in the 1st column. It is necessary for generating
names of files etc.

3rd column contains numbers of columns (excluding the 1st one) from weather data files that contain climate element's 
values that are useful for future analisys. All the other columns are deleted from the data set in the course of
program.
"""
observedCharacteristics = [
    ['air_temperature', 'TU',[3,4]],                #0
    ['cloudiness', 'N',[4]],                        #1
    ['precipitation', 'RR',[3]],                    #2
    ['pressure', 'P0',[3,4]],                       #3
    ['soil_temperature', 'EB',[3,4,5,6,7,8]],       #4
    ['solar', 'ST',[3,4,5,6,7]],                    #5
    ['sun', 'SD',[3]],                              #6
    ['wind', 'FF',[3,4]]                            #7
]

#Path to the directory with files downloaded from the FTP server
dirpath_downloaded = 'data/download/'

#Format of the timestamp used in the program (based on the format used in the weather data)
fmt = '%Y%m%d%H'




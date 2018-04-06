"""
This module contains default input parameters (settings) for the program, as well, as some
defined variables that are used by various modules of the program.
"""
import os
import pickle

"""
Variable defining if the program can use weather data previously downloaded from the FTP server
and stored on the local drive. If the value is set to 0, when searching for weather data, program will
connect to the DWD FTP server and download files from there. Therefore internet connection is required.

If the value is set to 1, program will search directory defined in dirpath_offline in search for weather data.
Default value for dirpath_offline is empty and has to be set by the user.
The folder hierarchy there must be the same as on the FTP Server.
"""
use_offline_data = 0

dirpath_offline = ''

"""
Variables storing information about details of the connection to the DWD ftp server.
"""
ftp_dirpath = '/pub/CDC/observations_germany/climate/hourly/'

ftp_adress = 'ftp-cdc.dwd.de'

ftp_user = 'anonymous'

ftp_pass = ''

"""
Variable defining place on the hard drive where all the data will be stored. That includes downloaded files,
reports etc
"""
dirpath_program = os.getcwd()

dirpath_downloaded = dirpath_program + os.sep + 'data' + os.sep + 'download' + os.sep

output_directory = dirpath_program + os.sep +'output'+os.sep

output_filename = 'Output.epw'

output_path = output_directory + output_filename

"""
Variable controlling if the testing mode is on. If it's off, the program generates data basing on the year and 
coordinates using stored in an appropriate place on local drive or FTP server.
If it's on, then the program uses data from txt files stored in data/testing directory
"""
testing_mode = 0

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


"""
Format of the timestamp used in the program (based on the format used in the weather data filenames ETC)
"""
fmt = '%Y%m%d%H'

"""
Minimum number of data records in the given year (maximum 24*366 = 8784) for which the
data set is perceived as valid. If the station provides us with the data set with lower number of records
for the given year, it's perceived as invalid and added to the "forbidden" list.

"""
min_rec = 3000

"""
Variable defines whether or not output values in reports/converted_data and reports/raw_data
are saved in a tabular form with headers describing values in columns and their units.
This takes longer computational time.
"""
tabular_reports = True


"""
Default input parameters
"""
year = 2016
lon = 13.34
lat = 50.91
cityname = 'Dresden'
regionname = 'Saxony'
country = 'DE'
elevation = '113'

"""
Style of font used in GUI
"""
font_style = 'MS Schell DLG 2'
font_size = 8

def load_settings():
    """
    Function that reads previously saved settings from the serialization file.
    """
    try:
        settings = pickle.load(open('programdata'+os.sep+'settings.pickle','rb'))
        globals().update(settings)
    except:
        pass


def save_settings():
    """
    Function that saves settings for use in the following runs of the program.
    """
    global year, lon, lat
    global use_offline_data, dirpath_offline
    global ftp_dirpath, ftp_adress, ftp_user, ftp_pass
    global output_directory
    global cityname, regionname, elevation, country
    global min_rec
    global tabular_reports

    settings = {'year': year, 'lon': lon, 'lat': lat, 'use_offline_data': use_offline_data,
                'dirpath_offline': dirpath_offline, 'ftp_dirpath':ftp_dirpath, 'ftp_adress':ftp_adress,
                'ftp_user':ftp_user, 'ftp_pass': ftp_pass, 'output_directory': output_directory,
                'output_path': output_path, 'cityname': cityname, 'regionname': regionname, 'elevation': elevation,
                'country': country, 'min_rec': min_rec, 'tabular_reports': tabular_reports}

    try:
        pickle.dump(settings,open('programdata'+os.sep+'settings.pickle','wb'))
    except:
        pass
import os
import pickle

#Input parameters
year = 2016
lon = 13.34
lat = 50.91


"""
Variable defining if the program can use weather data previously downloaded from the FTP server
and stored on the local drive. If the value is set to 0, when searching for weather data, program will
connect to the DWD FTP server and download files from there. Therefore internet connection is required.

If the value is set to 1, program will search directory defined in dirpath_offline in search for weather data
The folder hierarchy there must be the same as on the FTP Server
"""
use_offline_data = 0

# dirpath_offline = 'E:\\DOKUMENTY\\WeatherData\\'

dirpath_offline = ''

"""
Variable storing path to the directory with hourly climate data on the FTP server
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

#Path to the directory with files downloaded from the FTP server
dirpath_downloaded = dirpath_program + '/data/download/'

#Format of the timestamp used in the program (based on the format used in the weather data)
fmt = '%Y%m%d%H'

#Minimum number of data records in the given year (maximum 24*366 = 8784) for which the
#data set is perceived as valid. If the station provides us with the data set with lower number of records
#for the given year, it's perceivd as invalid and added to the "forbidden" list
min_rec = 3000


headers_raw_data = [
    ['Date','Air Temp. [*C]','Rel. humid. [%]'],
    ['Date','Total cloud cover [1/8]'],
    ['Date','Hrly precipitation height [mm]'],
    ['Date','Mean sea level pressure [hPa]','Pressure at station height [hPa]'],
    ['Date','T at depth [*C]: 2 cm','5 cm','10 cm','20 cm','50 cm','100 cm'],
    ['Date','Hrly longwave dwnwrd rad. [J/cm2]','Hrly diff solar rad. [J/cm2]','Hrly solar incoming rad. [J/cm2]',
     'Sunshine duration [min]','Zenith angle [*]'],
    ['Date','Sunshine duration [min]'],
    ['Date','Wind speed [m/s]','Wind direction [Grad]']
]

headers_converted_data = [
    ['Date','(r)Air Temp. [*C]','(r)Rel. humid. [%]','Dry Bulb Temp. [*C]','Dew Point Temp [*C]', 'Rel. Humid. [%]'],
    ['Date','(r)Total cloud cover [1/8]','Total Sky Cover [1/10]'],
    ['Date','(r)Hrly precipitation height [mm]'],
    ['Date','(r)Mean sea level pressure [hPa]','(r)Pressure at station height [hPa]','Atmosphetic Station Pressure [Pa]'],
    ['Date','(r)T at depth [*C]: 2 cm','(r)5 cm','(r)10 cm','(r)20 cm','(r)50 cm','(r)100 cm'],
    ['Date','(r)Hrly longwave dwnwrd rad. [J/cm2]','(r)Hrly diff solar rad. [J/cm2]','(r)Hrly solar incoming rad. [J/cm2]',
     '(r)Sunshine duration [min]','(r)Zenith angle [*]','Diff. Horiz. Irrad. [W/m2]','Glob. Horiz. Irrad. [W/m2]',
     'Dir. Norm. Irrad. [W/m2]','Horiz. Infrared Radiat. Intens. [W/m2]'],
    ['Date','(r)Sunshine duration [min]'],
    ['Date','(r)Wind speed [m/s]','(r)Wind direction [Grad]','Wind Direction [*]','Wind Speed [m/s]']
]

stage_name = 'Click START to proceed.'
stage_percent = 0

def setStatus(stage_name_new,stage_percent_new):
    global stage_name
    stage_name = stage_name_new
    stage_percent = stage_percent_new

min_year = 1958
max_year = 2017

#Output path for .epw file


output_directory = dirpath_program + os.sep +'output'
output_filename = 'Output.epw'
output_path = output_directory + os.sep + output_filename

cityname = 'Dresden'
regionname = 'Saxony'
country = 'DE'
elevation = '113'

def load_settings():
    try:
        settings = pickle.load(open('programdata/settings.pickle','rb'))
        globals().update(settings)
    except:
        pass

def save_settings():
    global year, lon, lat
    global use_offline_data, dirpath_offline
    global ftp_dirpath, ftp_adress, ftp_user, ftp_pass
    global output_directory
    global cityname, regionname, elevation, country

    settings = {'year': year, 'lon': lon, 'lat': lat, 'use_offline_data': use_offline_data,
                'dirpath_offline': dirpath_offline, 'ftp_dirpath':ftp_dirpath, 'ftp_adress':ftp_adress,
                'ftp_user':ftp_user, 'ftp_pass': ftp_pass, 'output_directory': output_directory,
                'output_path': output_path, 'cityname': cityname, 'regionname': regionname, 'elevation': elevation,
                'country': country}

    try:
        pickle.dump(settings,open('programdata/settings.pickle','wb'))
    except:
        pass
import os
import math
from Settings import *
from prettytable import PrettyTable
from pathlib import Path
import ftplib

def create_stations_list():
    stations_list = []

    # dirpath = os.path.abspath(os.curdir)

    for characteristics in observedCharacteristics:
        char_name = characteristics[0]
        char_short = characteristics[1]
        filename = char_short+'_Stundenwerte_Beschreibung_Stationen.txt'
        idlist_files = []  # list with IDs of stations with zip files in historical folder
        dateslist_historical = []  # list of dates of ends of historical data

        if use_offline_data:
            if (char_name != 'solar'):
                folderpath = dirpath_offline + char_name + '\\historical\\'
            else:
                folderpath = dirpath_offline + char_name + '\\'

            filepath = folderpath + filename
            fileslist = os.listdir(folderpath)

        else:
            # Connecting to the server
            try:
                ftp = ftplib.FTP('ftp-cdc.dwd.de')
                ftp.login(user='anonymous', passwd='')
            except Exception:
                print('Unable to connect to FTP server')

            if char_name != "solar":
                path_ftp = dirpath_ftp + char_name + '/historical/'
            else:
                path_ftp = dirpath_ftp + char_name + '/'

            ftp.cwd(path_ftp)

            path_local = dirpath_downloaded + char_name+ '/'
            ftp.cwd(path_ftp)
            filepath = path_local + filename

            if Path(filepath).is_file():
                continue
            # If the file does not exist, download process proceeds
            else:
                file = open(filepath, 'wb')
                try:
                    ftp.retrbinary('RETR %s' % filename, file.write)
                except Exception:
                    print('Unable to download Beschreibung file from FTP server')
                file.close()

            ls = []
            ftp.retrlines('MLSD', ls.append)  # listing files in the directory
            fileslist = []
            for line in ls:
                line_splitted = line.split(";")
                for line_inner in line_splitted:
                    if str(line_inner).strip().endswith('.zip'):
                        fileslist.append(str(line_inner).strip())

            ftp.quit()

        file = open(filepath, 'r')
        whole_file = file.readlines()
        file.close()


        for file in fileslist:
            if file.endswith(".zip"):
                filename_zip = file.split('_')
                idlist_files.append(filename_zip[2])
                if char_name != 'solar':
                    dateslist_historical.append(filename_zip[4])
                else:
                    dateslist_historical.append(past_year+'1231')
        # creating list of files in the folder to extract the ending date of "historical" weather data which is "hidden"
        # in the zip file name
        #this is also needed to check if the data from the station on the list is actually available as a zip file

        station = []
        historical_list_pointer = 0
        # Skipping first two lines not consist of station data
        # Going over every line in the file
        for i in range(2, len(whole_file)):
            splitted = whole_file[i].split()  # splitting the single line of the list
            # The line of the file has been splitted where empty spaces occur
            # Some stations however have empty spaces in their names
            # The following code deals with that problem
            if (len(splitted) > 8):
                override = len(splitted) - 8
                bundesland = splitted[len(splitted) - 1]

                #putting the name of the city together
                name = ''
                for j in range(0, override + 1):
                    if (j == 0):
                        name = name + splitted[6 + j]
                    else:
                        name = name + ' ' + splitted[6 + j]

                splitted[6] = name
                splitted[7] = bundesland

                # Deleting no longer necessary elements of the splitted line
                for j in range(0, override):
                    del splitted[-1]

            #default values for parameters mentioned below is 0
            splitted.append(0)  # splitted[8] is_in_historical
            splitted.append(0)  # splitted[9] date_end_historical

            if splitted[0] in idlist_files:
                splitted[8] = 1
                splitted[9] = dateslist_historical[historical_list_pointer]
                historical_list_pointer += 1

            #if the station does not exists in the weather data, it wont be added to the list
            if(splitted[8] != 0):
                station.append(splitted)

        stations_list.append(station)


    return stations_list


# Function that creates appropriate list depending on the choosen year
def year_appropriate_stations_list(year, list):
    startdate = int(str(year) +'0101')
    enddate = int(str(year)+'1231')
    newlist = []
    for i in range(0, observations_number):
        newlistinner = []
        for station in list[i]:
            if(use_recent_data):
                if int(station[1]) <= startdate and int(station[9]) >= enddate:
                    newlistinner.append(station)
            else:
                if int(station[1]) <= startdate and int(station[2]) >= enddate:
                    newlistinner.append(station)
        newlist.append(newlistinner)

    return newlist


def gpsdistance(lat1,lon1,lat2,lon2):
    R = 6371000
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    dlat = abs(lat1-lat2)
    dlon = abs(lon1-lon2)
    dlon = math.radians(dlon)

    a = (math.sin(0.5 * dlat)) ** 2 + math.cos(lat1) * math.cos(lat2) * (math.sin(0.5 * dlon)) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R*c

def getbeststations(lat,lon,year):
    list = create_stations_list()
    yearlist = year_appropriate_stations_list(year, list)
    beststations = []
    for list in yearlist:
        distancemax = 99999999999
        beststation = []
        for station in list:
            distance =  gpsdistance(lat,lon,float(station[4]),float(station[5]))
            if distance < distancemax:
                distancemax = distance
                beststation = station
        beststations.append(beststation)

    for x in range(0,len(observedCharacteristics)):
        beststations[x].insert(0,observedCharacteristics[x][0])

    # print(beststations)
    t = PrettyTable(['Char','ID','DateStart','DateEnd','Elev.','Lat.','Lon.','City','Bundesland','in_hist','end_hist'])


    for x in range(0,len(observedCharacteristics)):
        t.add_row(beststations[x])

    return beststations, t
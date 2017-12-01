import os
import math


class Station:
    def __init__(
            self,
            stationID,
            stationElevation,
            stationLatitude,
            stationLongitude,
            stationName,
            stationState):
        self.stationID = stationID
        self.stationElevation = stationElevation
        self.stationLatitude = stationLatitude
        self.stationLongitude = stationLongitude
        self.stationName = stationName
        self.stationState = stationState

        # setting the default start and ending dates of specific observations
        # they are set to high (low) number by default
        self.startingDates = []
        self.endingDates = []

        for i in range(0, 8):
            self.startingDates.append(99999999)
            self.endingDates.append(0)


observedCharacteristics = [
    ['air_temperature', 'TU'],
    ['cloudiness', 'N'],
    ['precipitation', 'RR'],
    ['pressure', 'P0'],
    ['soil_temperature', 'EB'],
    ['solar', 'ST'],
    ['sun', 'SD'],
    ['wind', 'FF']
]

observations_number = len(observedCharacteristics)

use_recent_data = 0

def createstationlist():
    stations_big_list = []

    # dirpath = os.path.abspath(os.curdir)
    dirpath = 'E:\\DOKUMENTY\\WeatherData\\'

    for characteristics in observedCharacteristics:
        # Absolute path to the file with station list
        # Solar data are not separated in recent and historical - therefore the if clause
        if (characteristics[0] != 'solar'):
            folderpath_historical = dirpath + characteristics[0] + '\\historical\\'
            folderpath_recent = dirpath + characteristics[0] + '\\recent\\'
            filepath = dirpath + characteristics[0] + '\\historical\\' \
                       + characteristics[1] + '_Stundenwerte_Beschreibung_Stationen.txt'
        else:
            folderpath_recent = dirpath + characteristics[0]
            filepath = dirpath + characteristics[0] + '\\' \
                       + characteristics[1] + '_Stundenwerte_Beschreibung_Stationen.txt'

        # creating list of files in the folder to extract the ending date of "historical" weather data which is "hidden"
        # in the zip file name
        #this is also needed to check if the data from the station on the list is actually available as a zip file
        if characteristics[0] is not 'solar':
            fileslist_historical = os.listdir(folderpath_historical)
            idlist_historical = []
            dateslist_historical = []
            for file in fileslist_historical:
                if file.endswith(".zip"):
                    filename = file.split('_')
                    idlist_historical.append(filename[2])
                    dateslist_historical.append(filename[4])

        fileslist_recent = os.listdir(folderpath_recent)
        idlist_recent = []
        for file in fileslist_recent:
            if file.endswith(".zip"):
                filename = file.split('_')
                idlist_recent.append(filename[2])

        #reading the file with the station list
        file = open(filepath, 'r')
        whole_file = file.readlines()
        file.close()
        stations_small_list = []

        historical_list_pointer = 0
        # Skipping first two lines not consistin gof station data
        # Going over every line in the file
        for i in range(2, len(whole_file)):
            splitted = whole_file[i].split()  # splitting the single line of the list
            # The line of the file has been splitted where empty spaces occur
            # Some stations however have empty spaces in their names
            # The following code deals with that problem
            if (len(splitted) > 8):
                override = len(splitted) - 8
                bundesland = splitted[len(splitted) - 1]

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

            splitted.append(0)  # splitted[8] is_in_historical
            splitted.append(0)  # splitted[9] date_end_historical
            splitted.append(0)  # splitted[10] is_in_recent

            if splitted[0] in idlist_historical:
                splitted[8] = 1
                splitted[9] = dateslist_historical[historical_list_pointer]
                historical_list_pointer += 1

            if splitted[0] in idlist_recent:
                splitted[10] = 1

            stations_small_list.append(splitted)

        stations_big_list.append(stations_small_list)


    return stations_big_list


fulllist = createstationlist()

# Function that creates appropriate list depending on the choosen year
def yearappropriatelist(year, list):
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


year = 2016
yearlist = yearappropriatelist(year, fulllist)

def gpsdistance(lon1,lat1,lon2,lat2):
    R = 6371000
    lon1 = math.radians(lon1)
    lon2 = math.radians(lon2)

    dlon = abs(lon1-lon2)
    dlat = abs(lat1-lat2)
    dlat = math.radians(dlat)

    a = (math.sin(0.5 * dlat)) ** 2 + math.cos(lat1) * math.cos(lat2) * (math.sin(0.5 * dlon)) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R*c
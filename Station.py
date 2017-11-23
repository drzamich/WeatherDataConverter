import os


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


def createstationlist():
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


    observations_number = 8

    stations_id_list = []
    stations_big_list = []
    dirpath = os.path.abspath(os.curdir)

    for characteristics in observedCharacteristics:
        a=0
        # Absolute path to the file with station list
        # Solar data are not separated in recent and historical
        if (characteristics[0] != 'solar'):
            filepath = dirpath + '\\data\\offline\\' + characteristics[0] + '\\historical\\' \
                       + characteristics[1] + '_Stundenwerte_Beschreibung_Stationen.txt'
        else:
            filepath = dirpath + '\\data\\offline\\' + characteristics[0] + '\\' \
                       + characteristics[1] + '_Stundenwerte_Beschreibung_Stationen.txt'

        file = open(filepath, 'r')
        whole_file = file.readlines()
        file.close()
        stations_small_list = []
        observed_ids = []
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

            stations_small_list.append(splitted)
            stations_id_list.append(splitted[0])

        stations_big_list.append(stations_small_list)

    stations_id_list_sorted = []
    for id in stations_id_list:
        if id not in stations_id_list_sorted:
            stations_id_list_sorted.append(id)

    real_stations_list = []

    saved_ids = []
    for i in range(0, observations_number):
        for station in stations_big_list[i]:
            if station[0] not in saved_ids:
                real_stations_list.append([station[0], station[3], station[4], station[5], station[6], station[7]])



    for i in range(0, observations_number):
        a=0
        for id in stations_id_list_sorted:
            startdate=99999999
            enddate=0
            for station in stations_big_list[i]:
                if id == station [0]:
                    startdate = station[1]
                    enddate = station[2]

            real_stations_list[a].append(startdate)
            real_stations_list[a].append(enddate)
            a += 1


createstationlist()

from Station import *
from Data import *
from datetime import datetime

year = 2015
lat = 52.93
lon = 8.23


if __name__=="__main__":
    generate_report(1)
    station_list, stations_table = getbeststations(lat,lon,year)

    report_text = ('Data extraction executed at %s \n' % str(datetime.now())
    +'Choosen year: %s \n' %str(year)
    +'Latitude: %s \n' %str(lat)
    +'Lognitude: %s \n\n'%str(lon)
    +'List of most favourable weather stations: \n'
                    )
    generate_report(2,report_text)
    generate_report(2,str(stations_table))
    weather_data = create_weather_set(station_list,year)
    # print(station_list)



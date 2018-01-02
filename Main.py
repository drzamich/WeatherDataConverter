from Station import *
from Data import *

year = 2015
lat = 52.93
lon = 8.23


if __name__=="__main__":
    station_list = getbeststations(lat,lon,year)
    weather_data = create_weather_set(station_list,year)
    # print(station_list)



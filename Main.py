from Helping import *
from Settings import *
# from Station import *
# from Data import *
# from datetime import *
#
#
# if __name__=="__main__":
#     station_list, stations_table = getbeststations(lat,lon,year)
#
#     report_text = ('Data extraction executed at %s \n' % str(datetime.now())
#     +'Choosen year: %s \n' %str(year)
#     +'Latitude: %s \n' %str(lat)
#     +'Lognitude: %s \n\n'%str(lon)
#     +'List of most favourable weather stations: \n'
#                     )
#     generate_report(mode=1,text=report_text)
#     generate_report(mode=1,text=str(stations_table))
#     weather_data = create_weather_set(station_list,year)


import StationSearcher

explo = StationSearcher.StationSearcher(2016, 52.93, 8.23)

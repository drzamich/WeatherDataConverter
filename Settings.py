use_recent_data= 0
use_offline_data = 1

observedCharacteristics = [
    ['air_temperature', 'TU',[3,4]],
    ['cloudiness', 'N',[4]],
    ['precipitation', 'RR',[3]],
    ['pressure', 'P0',[3,4]],
    ['soil_temperature', 'EB',[3,4,5,6,7,8]],
    ['solar', 'ST',[3,4,5,6,7]],
    ['sun', 'SD',[3]],
    ['wind', 'FF',[3,4]]
]


observations_number = len(observedCharacteristics)

dirpath_offline = 'E:\\DOKUMENTY\\WeatherData\\'
dirpath_ftp = '/pub/CDC/observations_germany/climate/hourly/'


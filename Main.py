import StationSearcher
import DataReader
import DataConverter
import Reporter

#Defining input parameters for extracting weather data
#In the later version of the program this will be done in the user interface
year = 2016
lat = 52.93
lon = 8.23

if __name__ == '__main__':
    #Calling the StationSearcher constructor using input parameters
    searcher = StationSearcher.StationSearcher(year, lat, lon)
    #Output -  list of 7 stations that are most favourable for given input paramaters, saved in variable station_list
    station_list = searcher.station_list

    #Calling the DataReader constructor using previously created station list
    extractor = DataReader.DataReader(year, station_list)
    #Output - unconverted set of data extracted from zip files in the form of list
    extracted_data = extractor.raw_data_set

    #Calling the DataConverter constructor using previously created raw data
    convertor = DataConverter.DataConverter(year, extracted_data)
    #Output: converted data with calculated additional values needed in energy analisys programs
    converted_data = convertor.converted_data
    #Additionally, periods with missing entries in the original data set as well as number of those enries are saved
    missing_list = convertor.missing_list                       #list with missing periods
    missing_entries_list = convertor.missing_entries_list       #list with number of missing entries

    #Calling the Reporter class that based on the data generated in steps before, creates report files in the reports/
    #directory
    reporter = Reporter.Reporter(year, lon, lat, station_list, missing_list, missing_entries_list,
                             converted_data)
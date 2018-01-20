import StationSearcher
import DataReader
import DataConverter
import Reporter

year = 2016
lat = 52.93
lon = 8.23

if __name__ == '__main__':
    searcher = StationSearcher.StationSearcher(year, lat, lon)
    station_list = searcher.station_list

    extractor = DataReader.DataReader(year, station_list)
    extracted_data = extractor.raw_data_set

    convertor = DataConverter.DataConverter(year, extracted_data)
    converted_data = convertor.converted_data
    missing_list = convertor.missing_list
    missing_entries_list = convertor.missing_entries_list

    reporter = Reporter.Reporter
    reporter.generate_report_raw_data(reporter, year, lon, lat, station_list, missing_list, missing_entries_list,
                                      converted_data)

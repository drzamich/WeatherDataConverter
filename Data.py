from Settings import *
import zipfile

def create_weather_set(station_list,year):
    temp_list = []
    #creating list of air temperatures and humidity

    zip_filepath = dirpath + observedCharacteristics[0][0] + '\\historical\\stundenwerte_TU_'+station_list[0][0]+'_'\
               + station_list[0][1]+'_'+station_list[0][9]+'_hist.zip'

    txt_filename = 'produkt_tu_stunde_'+station_list[0][1]+'_'+station_list[0][9]+'_'+station_list[0][0]+'.txt'

    zf = zipfile.ZipFile(zip_filepath)
    fileopen = zf.open(txt_filename)
    txt_file = fileopen.readlines()


    for line in txt_file:
        #splitting each line of the file where the semicolon is. also decoding the file from bytes to utf8 format
        line_splitted = line.decode('utf8').split(";")
        date = line_splitted[1]
        temp_list_entry = []
        if (date.startswith(str(year))):
            temp_list_entry.append(date[0:4])
            temp_list_entry.append(date[4:6])
            temp_list_entry.append(date[6:8])
            temp_list_entry.append(date[8:10])
            temp_list_entry.append(line_splitted[3].strip())
            temp_list_entry.append(line_splitted[4].strip())
            temp_list.append(temp_list_entry)

    print(len(temp_list))
    fix_data_list(temp_list)

#function that searches the given list with weather data for missing hours. then it interpolates the neighbouring
#values and puts inside the list
def fix_data_list(data_list):

    for index,entry in enumerate(data_list):
        if(index!=0):
            hour_diff = int(data_list[index][3]) - int(data_list[index-1][3])
            if(hour_diff != 1 and hour_diff != -23):
                print(index,entry)
    # print(zip_filepath)
    # print(txt_filename)
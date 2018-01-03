from Settings import *
from datetime import datetime, timedelta
import zipfile
from Helping import *


def create_weather_set(station_list,year):
    temp_hum_list = get_temp_data(station_list,year)

# creating list of air temperatures and humidity
def get_temp_data(station_list,year):
    temp_list = []

    zip_filepath = dirpath + observedCharacteristics[0][0] + '\\historical\\stundenwerte_TU_'+station_list[0][1]+'_'\
               + station_list[0][2]+'_'+station_list[0][10]+'_hist.zip'

    txt_filename = 'produkt_tu_stunde_'+station_list[0][2]+'_'+station_list[0][10]+'_'+station_list[0][1]+'.txt'

    zf = zipfile.ZipFile(zip_filepath)
    fileopen = zf.open(txt_filename)
    txt_file = fileopen.readlines()

    for line in txt_file:
        #splitting each line of the file where the semicolon is. also decoding the file from bytes to utf8 format
        line_splitted = line.decode('utf8').split(";")
        date = line_splitted[1]
        temp_list_entry = []
        if (date.startswith(str(year))):
            temp_list_entry.append(date)
            temp_list_entry.append(line_splitted[3].strip())
            temp_list_entry.append(line_splitted[4].strip())
            temp_list.append(temp_list_entry)

    temp_hum_list, missing_list = interpolate_data_list(temp_list, [1,2])

    report_text = '\n \n Extracting air_temp and humidity data \n There are missing values between pairs of dates:'
    for i in range(0,len(missing_list)):
        report_text += '\n'+ str(missing_list[i])

    generate_report(2,report_text)

    return temp_hum_list

#Function that searches the given data list for missing hours
#Then it interpolates the values based on the records neighbouting to missing values and inserts them in the middle
#of the list
#Interpolated values are stored in the "columns"

def interpolate_data_list(data_list, columns):
    missing_list = []
    for index,entry in enumerate(data_list):
        if(index!=0):
            #to check if any values are missing, the time difference between two entries is calculated
            #if the time fidderence in hours is bigger than 1, that means there is a missing value

            #putting the date togehter out of the data in the list
            date1 = data_list[index-1][0]
            date2 = data_list[index][0]

            fmt = '%Y%m%d%H' #format of the timestamp
            tstamp1 = datetime.strptime(date1,fmt)
            tstamp2 = datetime.strptime(date2,fmt)

            td = tstamp2 - tstamp1

            td_hours = td.total_seconds()/3600

            new_values = []
            #if the time diff between dates is bigger than 1, that means there is a missing value
            if td_hours > 1.0:
                print('elo')
                missing_list.append([date1,date2])
                for column in columns:
                    new_values_entry = []
                    value1 = float(data_list[index-1][column])
                    value2 = float(data_list[index][column])
                    incr = (value2 - value1)/td_hours
                    for x in range(1,int(td_hours)):
                        new_values_entry.append(value1+x*incr)
                    new_values.append(new_values_entry)

                #inserting calculated values to the original list
                for x in range(1,int(td_hours)):
                    new_entry = []
                    date1 = data_list[index-1][0]

                    tstamp1 = datetime.strptime(date1,fmt)

                    tstamp_new = tstamp1+timedelta(hours=x)

                    date_new = datetime.strftime(tstamp_new,fmt)

                    new_entry.append(date_new)
                    for i in range(0,len(columns)):
                        new_entry.append(new_values[i][x-1])

                    data_list.insert((index-1)+x,new_entry)

    save_list_to_file(data_list,'lala.txt')
    print(missing_list)
    return data_list, missing_list

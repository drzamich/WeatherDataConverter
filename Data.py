from Settings import *
from datetime import datetime, timedelta
import zipfile
from Helping import *
import os
import ftplib

def create_weather_set(station_list,year):
    get_solar_data(station_list,year)
    # temp_hum_list = get_temp_data(station_list,year)

# creating list of air temperatures and humidity
# def get_temp_data(station_list,year):
    # temp_list = []
    #
    #
    #
    # txt_filename = 'produkt_tu_stunde_'+station_list[0][2]+'_'+station_list[0][10]+'_'+station_list[0][1]+'.txt'
    #
    # zf = zipfile.ZipFile(zip_filepath)
    # fileopen = zf.open(txt_filename)
    # txt_file = fileopen.readlines()
    #
    # for line in txt_file:
    #     #splitting each line of the file where the semicolon is. also decoding the file from bytes to utf8 format
    #     line_splitted = line.decode('utf8').split(";")
    #     date = line_splitted[1]
    #     temp_list_entry = []
    #     if (date.startswith(str(year))):
    #         temp_list_entry.append(date)
    #         temp_list_entry.append(line_splitted[3].strip())
    #         temp_list_entry.append(line_splitted[4].strip())
    #         temp_list.append(temp_list_entry)
    #
    # temp_hum_list, missing_list = interpolate_data_list(temp_list, [1,2])
    #
    # report_text = '\n \n Extracting air_temp and humidity data \n There are missing values between pairs of dates:'
    # for i in range(0,len(missing_list)):
    #     report_text += '\n'+ str(missing_list[i])
    #
    # generate_report(2,report_text)
    #
    # return temp_hum_list

def get_solar_data(station_list,year):
    get_data_file(5,station_list[5][1])
    # solar_list = []
    #
    # zip_filepath = dirpath + observedCharacteristics[5][0] + '\\stundenwerte_ST_'+station_list[5][1]+'_'\
    #            + station_list[5][2]+'_'+station_list[5][10]+'_row.zip'
    #
    # txt_filename = 'produkt_st_stunde_'+station_list[0][2]+'_'+station_list[0][10]+'_'+station_list[0][1]+'.txt'
    #
    # zf = zipfile.ZipFile(zip_filepath)
    # fileopen = zf.open(txt_filename)
    # txt_file = fileopen.readlines()
    #
    # for line in txt_file:
    #     #splitting each line of the file where the semicolon is. also decoding the file from bytes to utf8 format
    #     line_splitted = line.decode('utf8').split(";")
    #     date = line_splitted[1]
    #     temp_list_entry = []
    #     if (date.startswith(str(year))):
    #         temp_list_entry.append(date)
    #         temp_list_entry.append(line_splitted[3].strip())
    #         temp_list_entry.append(line_splitted[4].strip())
    #         temp_list.append(temp_list_entry)
    #
    # temp_hum_list, missing_list = interpolate_data_list(temp_list, [1,2])
    #
    # report_text = '\n \n Extracting air_temp and humidity data \n There are missing values between pairs of dates:'
    # for i in range(0,len(missing_list)):
    #     report_text += '\n'+ str(missing_list[i])
    #
    # generate_report(2,report_text)
    #
    # return temp_hum_list

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


def get_data_file(characteristic_num,station_id,year=None):

#Function that, based on the characteristic number and station id, finds on the FTP server
#The proper zip file with weather data, downloads and opens it, opens the data file and extracts from it the data
#For the given year
    characteristic_name = observedCharacteristics[characteristic_num][0]
    characteristic_short = observedCharacteristics[characteristic_num][1]

    #Defining the begining of the file name and the directory on the server based on the station ID

    filename_begin = 'stundenwerte_' + characteristic_short.upper() + '_' + station_id

    if characteristic_num!=5:
        path = dirpath_ftp + characteristic_name + '\\historical\\'
    else:
        path = dirpath_ftp + characteristic_name

    #Connecting to the server
    try:
        ftp = ftplib.FTP('ftp-cdc.dwd.de')
        ftp.login(user='anonymous',passwd='')
    except Exception:
        print('Unable to connect to FTP server')

    ftp.cwd(path) #changing the directory
    ls = []
    ftp.retrlines('MLSD',ls.append)  #listing files in the directory

    #looking for the file that's name begins with out defined string
    for line in ls:
        line_splitted = line.split(";")
        for line_inner in line_splitted:
            if str(line_inner).strip().startswith(filename_begin):
                filename = str(line_inner).strip()
    #downloading the zip

    file = open('data/'+filename, 'wb')
    try:
        ftp.retrbinary('RETR %s' % filename, file.write)
    except Exception:
        print('Unable to download file from FTP server')

    file.close()

    ftp.quit()

    #opening the zip file
    zf = zipfile.ZipFile('data/'+filename)

    list = zf.namelist()

    for item in list:
        if str(item).startswith('produkt'):
            file_data_name = str(item)

    file_data = zf.open(file_data_name)
    temp_file_data = open('data/'+characteristic_short+'.txt','w')

    list = file_data.readlines()
    for line in list:
        temp_file_data.write(line.encode('utf-8'))

    temp_file_data.close()
    file_data.close()

    # removing the zip file
    zf.close()
    os.remove('data/'+filename)

    return file_data
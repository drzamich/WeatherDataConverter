import zipfile
from Helping import *
import ftplib
import math
import os
from pathlib import Path
from datetime import *

def create_weather_set(station_list,year):
    generate_raw_data(station_list,year)

def generate_raw_data(station_list,year):
    if not use_offline_data:
        download_data_from_server(station_list)

    missing_values_list = []
    for index,char in enumerate(observedCharacteristics):

        char_name = observedCharacteristics[index][0]
        raw_data_list = get_data_from_file(index,station_list[index][1],year)
        interpolated_data_list, missing_values_entry = interpolate_data_list(raw_data_list,index)

        missing_values_list.append(missing_values_entry)

        save_list_to_file(interpolated_data_list,'data/'+char_name+'.txt')

        report_text = ('\nSuccesfully extracted and interpolated data for '+char_name+'\n'
        +'There were %s periods with missing values \n' %len(missing_values_entry) )

        generate_report(mode=1,text=report_text)

    generate_report(mode=2,missing_values_list=missing_values_list)

#Function that searches the given data list for missing hours
#Then it interpolates the values based on the records neighbouting to missing values and inserts them in the middle
#of the list
#Interpolated values are stored in the "columns"

def interpolate_data_list(data_list,char_num):
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
                missing_list.append([date1,date2])
                for i in range(1,len(entry)):
                    new_values_entry = []
                    value1 = float(data_list[index-1][i])
                    value2 = float(data_list[index][i])
                    incr = (value2 - value1)/td_hours
                    for x in range(1,int(td_hours)):
                        if char_num==1:                                      #special case for interpolation of clouds
                            new_values_entry.append(math.ceil(value1+x*incr)) #the cloud cover has to be a  whole number
                        else:
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
                    for i in range(0,len(entry)-1):
                        new_entry.append(new_values[i][x-1])

                    data_list.insert((index-1)+x,new_entry)

    return data_list, missing_list


def download_data_from_server(station_list):

# This function downloads data from server in one go based on the staions IDs
# It only needs to connect to the server once, therefore it limits queries send to server that may leed to issues
# Like blocking the user

    # Connecting to the server
    try:
        ftp = ftplib.FTP('ftp-cdc.dwd.de')
        ftp.login(user='anonymous', passwd='')
    except Exception:
        print('Unable to connect to FTP server')

    for index,char in enumerate(observedCharacteristics):

        char_name = char[0]
        char_short = char[1]

        if index != 5:
            path = dirpath_ftp + char_name + '/historical/'
        else:
            path = dirpath_ftp + char_name

        ftp.cwd(path) #changing the directory
        ls = []
        ftp.retrlines('MLSD',ls.append)  #listing files in the directory

        station_id = station_list[index][1]
        filename_begin = 'stundenwerte_' + char_short.upper() + '_' + station_id

        #looking for the file that's name begins with our defined string
        for line in ls:
            line_splitted = line.split(";")
            for line_inner in line_splitted:
                if str(line_inner).strip().startswith(filename_begin):
                    filename = str(line_inner).strip()

        #checking if our file already exists in the download folder
        filepath = dirpath_downloaded + '/' + char_name + '/' + filename
        if Path(filepath).is_file():
            continue

        #If the file does not exist, download process proceeds
        else:
            file = open(filepath, 'wb')
            try:
                ftp.retrbinary('RETR %s' % filename, file.write)
            except Exception:
                print('Unable to download file from FTP server')

            file.close()

    ftp.quit()


def get_data_from_file(char_num, station_id, year):

#Function that, based on the characteristic number and station id, finds on the FTP server
#The proper zip file with weather data, downloads and opens it, opens the data file and extracts from it the data
#For the given year

    char_name = observedCharacteristics[char_num][0]
    char_short = observedCharacteristics[char_num][1]

    #Defining the begining of the file name and the directory on the server based on the station ID

    filename_begin = 'stundenwerte_' + char_short.upper() + '_' + station_id

    if use_offline_data:
        #use offline data
        if char_num != 5:  #not solar data
            path = dirpath_offline + char_name + '//historical//'
        else:               #solar data
            path = dirpath_offline + char_name+'/'

    else:
        path = dirpath_downloaded + char_name+'/'

    dir_list = os.listdir(path)

    for item in dir_list:
        if str(item).startswith(filename_begin):
            filename = str(item)

    zf = zipfile.ZipFile(path+filename)

    inside_zip = zf.namelist()

    #looking for txt file with the name produkt*
    for item in inside_zip:
        if str(item).startswith('produkt'):
            file_data_name = str(item)

    file_data = zf.open(file_data_name)

    file_data_as_list = file_data.readlines()
    file_data.close()
    file_data_year_list = extract_appropriate_year(file_data_as_list,year,char_num)

    zf.close()

    return file_data_year_list


def extract_appropriate_year(list,year,char_num):
# Function that when given a list resulting from data file, returns a list with data corresponding with the given year

    temp_list = []
    for line in list:
        #splitting each line of the file where the semicolon is. also decoding the file from bytes to utf8 format
        line_splitted = line.decode('utf8').split(";")
        date = line_splitted[1]
        temp_list_entry = []
        if (date.startswith(str(year))):
            temp_list_entry.append(date[0:10])
            for index in observedCharacteristics[char_num][2]:
                temp_list_entry.append(line_splitted[index].strip())

            temp_list.append(temp_list_entry)
    return temp_list
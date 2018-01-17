from Settings import *
import os

def save_list_to_file(list,filename):
    file = open(filename,"w")
    for entry in list:
        file.write(str(entry)+'\n')
    file.close

def generate_report(mode = None, text=None, missing_values_list = None, intepolated_data_list = None, missing_entries=None):
    dirpath = 'reports/'+current_date+'/'
    if not os.path.isdir(dirpath):
        os.mkdir(dirpath)
        os.mkdir(dirpath+'therakles/')

    if mode == 1 and text is not None:  # adding text to the report file

        f = open(dirpath+'00_report.txt','a')
        f.write(text)
        f.close

    elif mode == 2: #adding entries to the missing_values file

        f = open(dirpath+'00_missing_values.txt','a')

        for index,list in enumerate(missing_values_list):
            f.write(observedCharacteristics[index][0]+observedCharacteristics[index][1]+'\n')
            for item in list:
                f.write(str(item)+'\n')
            f.write('\n')

    elif mode == 3: #saving interpolated data to files
        for index,char in enumerate(observedCharacteristics):
            filepath = dirpath + char[0]+'.txt'
            f = open(filepath,'a')
            for entry in intepolated_data_list[index]:
                f.write(str(entry)+'\n')
            f.close()

def is_leap_year(year):
    if year % 4 == 0:
        return 1
    else:
        return 0

leap_year = is_leap_year(year)
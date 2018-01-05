from Settings import *
import os

def save_list_to_file(list,filename):
    file = open(filename,"w")
    for entry in list:
        file.write(str(entry)+'\n')
    file.close

def generate_report(mode = None,text=None, missing_values_list = None):
    dirpath = 'reports/'+current_date+'/'
    if not os.path.isdir(dirpath):
        os.mkdir(dirpath)

    if mode == 1 and text is not None:  # adding text to the report file

        f = open(dirpath+'report.txt','a')
        f.write(text)
        f.close

    elif mode == 2: #adding entries to the missing_values file

        f = open(dirpath+'MV.txt','a')

        for index,list in enumerate(missing_values_list):
            f.write(observedCharacteristics[index][0]+observedCharacteristics[index][1]+'\n')
            for item in list:
                f.write(str(item)+'\n')
            f.write('\n')

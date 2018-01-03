def save_list_to_file(list,filename):
    file = open(filename,"w")
    for entry in list:
        file.write(str(entry)+'\n')
    file.close

def generate_report(mode, text=None):
    if mode==1:  #clearing the report file
        f = open('report.txt',"w")
        f.close()
    if mode==2:   #reporting stations choosen for the analisys
        f = open('report.txt','a')
        # f.write(text.encode('utf-8'))
        f.write(text)
        f.close
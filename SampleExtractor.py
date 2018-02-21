extracted_fields = [13]
file_name = ''

for item in extracted_fields:
    file_name = file_name + str(item) + '_'

file_name = file_name[:-1]
file_name = file_name + '.txt'

source = open('data/output/sample_epw.txt')
listaaa = source.readlines()

output = open('data/output/'+file_name,'w')
for line in listaaa:
    items = line.split(',')
    year = str(items[0])
    month = str(items[1])
    day = str(items [2])
    hour = str(items[3])

    important = []
    for field in extracted_fields:
        important.append(items[field-1])
    new_item = [year+'/'+month+'/'+day+':'+hour,important]
    output.write(str(new_item)+'\n')

output.close()

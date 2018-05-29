#Fixes the dumb null characters that my home PC puts into the raw files.
def fix_bytes(filename):
    filepath = 'Net Array_Small.raw'
    l = []
    headerlen = 112
    with open(filename,'rb') as fp:
        for cnt, line in enumerate(fp):
            if cnt < headerlen:
                list_line = list(line)

                #Sometimes its even, sometimes its odd.
                if(list_line[0] == 0):
                    line = bytes(list_line[1::2])
                else:
                    line = bytes(list_line[::2])

            elif cnt == headerlen:
                list_line = list(line)
                line = bytes(list_line[1:])

            l.append(line)

    thefile = open('Net Array_Small.raw', 'wb')

    for line in l:
        thefile.write(line)

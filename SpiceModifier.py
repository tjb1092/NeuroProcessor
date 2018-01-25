import os

def GenerateLabels(outputPattern):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    fname = os.path.join(dir_path, 'SimInput','Template.asc')

    # Open Template & read into list
    with open(fname) as f:
        content = f.readlines()

    # Hard coded indicies to the PWL commands
    IndexList =[46, 52, 58, 64, 70, 76, 82, 88]

    #These can change to whatever. They are in Volts.
    labelPattern =[[1,5,1,5,1,5,1,5],
                   [4,2,4,2,4,2,4,2]]

    source_counter = 0
    for index in IndexList:
        #For each source, append the correct information per sample to the string.
        newString = "SYMATTR Value PWL("

        for row in outputPattern:
            if row[1] == 0:
                pattern = 0 # 1st and last voltage should be 0
            else:
                pattern = labelPattern[row[1]-1][source_counter] # Gets V1 or V2 pattern
            newString += " " + "{0:.3f}".format(row[0]) + " " + str(pattern)

        newString += ")\n"
        content[index] = newString #Override template w/ new command

        source_counter += 1

    voltage_element_fn = fname = os.path.join(dir_path, 'OutputLabels.asc')

    data_file = open(voltage_element_fn, "w")
    for line in content:
        data_file.write("%s" % line)
    data_file.close()
    print("Voltage Array Created!")

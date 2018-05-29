import os
import numpy as np
from FilterBankDesign import DesignFilterBank


def GenerateLabels(outputPattern, folderName):
    dir_path, content = SpiceReader('Template.asc')

    # Hard coded indicies to the PWL commands
    IndexList =[46, 52, 58, 64, 70, 76, 82, 88]

    #These can change to whatever is needed. They are in Volts.
    labelPattern =[[3,0,3,0,3,0,3,0],
                   [0,3,0,3,0,3,0,3]]

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

    # Write out newly modified file into the main directory
    voltage_element_fn = os.path.join(dir_path,'SimInput', folderName, 'OutputLabels.asc')
    SpiceWriter(content, voltage_element_fn)


def GenerateTestStartLabel(silence,testlength, folderName):
    dir_path, content = SpiceReader('StartTestLabel.asc')
    # Hard coded indicies to the Pulse command
    index = 8

    #Create new command
    newString = "SYMATTR Value PULSE(0 -12 " + "{0:.3f}".format(silence)+ " .01 .01 " + "{0:.3f}".format(testlength) + " " + "{0:.3f}".format(5+silence+testlength) + " 1)\n"
    print(newString)
    input("pause")
    content[index] = newString #Override template w/ new command


    # Write out newly modified file into the main directory
    voltage_element_fn = os.path.join(dir_path,'SimInput', folderName, 'StartTestLabel.asc')
    SpiceWriter(content, voltage_element_fn)


def GenerateFilterBank():
    dir_path, content = SpiceReader('FilterBank.asc')

    # Hard coded indicies to the Value commands
    R1IndexList =[291, 269, 325, 391, 369, 347, 435, 413]
    R2IndexList =[306, 284, 340, 406, 384, 362, 450, 428]
    R3IndexList =[550, 553, 556, 559, 547, 568, 562, 565]
    C1IndexList =[296, 274, 330, 396, 374, 352, 440, 418]
    C2IndexList =[301, 279, 335, 401, 379, 357, 445, 423]
    R4IndexList =[313, 457, 469, 481, 493, 505, 517, 529]
    R5IndexList =[318, 462, 474, 486, 498, 510, 522, 534]

    R1_val, R2_val, R3_val, C1_val, C2_val = DesignFilterBank()

    #Start w/ unity gain for inverting stage.

    R4_val = np.array([10000., 10000., 10000., 10000., 10000., 10000., 10000., 10000.])
    R5_val = np.array([10000., 10000., 10000., 10000., 10000., 10000., 10000., 10000.])

    content = FilterVal(R1_val, R1IndexList, content,False)
    content = FilterVal(R2_val, R2IndexList, content,False)
    content = FilterVal(R3_val, R3IndexList, content,False)
    content = FilterVal(C1_val, C1IndexList, content,True)
    content = FilterVal(C2_val, C2IndexList, content,True)
    content = FilterVal(R4_val, R4IndexList, content,False)
    content = FilterVal(R5_val, R5IndexList, content,False)

    # Write out newly modified file into the main directory
    voltage_element_fn = os.path.join(dir_path,'FilterBank.asc')
    SpiceWriter(content, voltage_element_fn)

def FilterVal(vals, indexList, content, isCap):
    counter = 0
    for index in indexList:
        #For each source, append the correct information per sample to the string.
        if isCap:
            val = vals[counter] * 1000000000.
            newString = "SYMATTR Value " + "{0:.3f}".format(val) + "n \n"
        else:
            newString = "SYMATTR Value " + "{0:.3f}".format(vals[counter]) + "\n"
        counter += 1
        content[index-1] = newString #Zero indexes a 1 indexed number
    return content



def SpiceWriter(content, voltage_element_fn):
    data_file = open(voltage_element_fn, "w")
    for line in content:
        data_file.write("%s" % line)
    data_file.close()
    print("Voltage Array Created!")

def SpiceReader(filename):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    fname = os.path.join(dir_path, 'SimInput',filename)

    # Open Template Circuit & read into list
    with open(fname) as f:
        content = f.readlines()

    return dir_path, content

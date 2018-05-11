import sys
import os
import pickle


"""
Tool to show the order of the generated sample patterns so that we can
troubleshoot particular sample numbers. Outputs response to a terminal.
"""

data = pickle.load(open( os.path.join('.', "SimInput", "data_info.p"), "rb" ) )
os.system('cls' if os.name == 'nt' else 'clear')

output = "\n \n"
for sample in data["Train"]:
    output = output + "|" + sample[0][44:-4]
output = output + "|-"

for sample in data["Test"]:
    output = output + "|" + sample[0][44:-4]

print(output + "|\n \n")

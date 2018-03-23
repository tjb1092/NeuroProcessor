import sys
import os
import pickle

data = pickle.load(open( os.path.join('.', "SimInput", "data_info.p"), "rb" ) )
os.system('cls' if os.name == 'nt' else 'clear')

output = "\n \n"
for sample in data["Train"]:
    output = output + "|" + sample
output = output + "|-"

for sample in data["Test"]:
    output = output + "|" + sample

print(output + "|\n \n")

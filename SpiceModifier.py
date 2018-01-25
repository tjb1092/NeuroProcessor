import os

# This will be automated later, just for testing.
num_elements = input("Please enter the number of voltage elements you want to have: ")

dir_path = os.path.dirname(os.path.realpath(__file__))
fname = os.path.join(dir_path, 'SimInput','Template.asc')

# Open Template & read into list
with open(fname) as f:
    content = f.readlines()

GndWire = content[3]
GndElement = content[6]
FirstVoltageElement = content[7] #Need this to know where to put subsequent elements

# Remove gnd element
del content[6]
del content[3]

print(GndWire)
print(GndElement)

VHeight = 112

# Hardcoding this just for convinience.
#I'm hardcoding the indicies in the template, so it's kinda the same thing.
Vstart = 48

WireStart = 32
GndStart = 144



# Extract coordinate parameters from the strings so that I can manipulate them.
GndWire_params = [int(s) for s in GndWire.split() if s.isdigit()]
GndElement_params = [int(s) for s in GndElement.split() if s.isdigit()]


PulseParams = [0,1,1,0.1,0.1,1,3,10]  #Test set for now
element_count = 0
for element in range(0,1):

    element_count += 1
    WireStart += 112
    Vstart += 112
    GndStart += 112
    # Block of content to write to schematic to add the new voltage element.
    # None string components need to be determined. (sleep now though).
    content.append("WIRE 64 "+str(WireStart+32)+" 64 "+str(WireStart))
    content.append("SYMBOL voltage 64 "+str(Vstart)+" R0")
    content.append("WINDOW 123 0 0 Left 2")
    content.append("WINDOW 39 0 0 Left 2")
    content.append("SYMATTR InstName V"+str(element_count+1))
    content.append("SYMATTR Value PULSE("+str(PulseParams[0])+" "+str(PulseParams[1])+" "+\
                    str(PulseParams[2])+" "+str(PulseParams[3])+" "+str(PulseParams[4])+" "+\
                    str(PulseParams[5])+" "+str(PulseParams[6])+" "+str(PulseParams[7])+")")
    content.append("WIRE 64 "+str(GndStart+16)+" 64 "+str(GndStart))
    content.append("FLAG 64 "+str(GndStart+16)+" 0")


    for line in content:
        print(line)

voltage_element_fn = fname = os.path.join(dir_path, 'SimInput','OutputLabels.asc')

data_file = open(voltage_element_fn, "w")
for line in content:
    data_file.write("%s\n" % line)
data_file.close()
print("Voltage Element Created!")

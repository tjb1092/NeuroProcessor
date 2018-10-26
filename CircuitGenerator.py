import numpy as np
from SpiceModifier import SpiceWriter

"""
# Going to generate a subcircuit that creates a perceptron spiking neural network.

# For now, it will be a single layer.

Initially, it will also be a single big circuit trying each layer individually.

m is the input dimensionality
n is the number of classes

# Need the following:
- Input Neuron layer Xni0 - Xnim
Neuron: input, output

i = vi0 - vim
o = niout0 - nioutm
model = liaf

- T-gate layer: Xtgate0 - Xtgatem | Xitgate0 - Xitgatem
Tgate: input, output, control

i = niout0 - nioutm
o = pre0 - prem | testpre0 - testprem
control = train
model = tgate | itgate

- mxn STRAM Array: Xsyn00 - Xsynmn
Synapse: pre, post, monitor

i = pre0 - prem
o = post0 - postn
monitor = mon00 - monmn

- mxn BStore Array: XB00 - XBmn
Bstore: pre, post, monitor, train

i = testpre0 - testprem
o = testpost0 - testpostn
state = vsyn00 - vsynmn
train = vTrain

- Bidirectional Amplifiers: Xbda0 - Xbdan
BDA: Vpost, Vnin, vnout, label
vpost =  post0 - postn
nin = vnin0 - vninn
nout = vnout0 - vnoutn
l = l0 - ln

- Output Neuron Layer: Xno0 - Xnon
Neuron: input, output
i = vnin0 - vninn
o = vnout0 - vnoutn
"""



def main():

    content = []

    num_features = 9
    num_classes = 8

    testMode = 5
    # First, I also need to add statements importing all of the models.

    # I can totally make this in one double loop. Just for now, I want to build it
    #up

    # Generate the input neuron layer:
    for m in range(num_features):
        new_string = "Xni{} vi{} niout{} liaf \n".format(m, m, m)
        content.append(new_string)


    if testMode > 1:
        # Generate T-gate layers
        for m in range(num_features):
            new_string = "Xtgate{} niout{} pre{} train tgate \n".format(m, m, m)
            content.append(new_string)
            new_string = "Xitgate{} niout{} testpre{} train itgate \n".format(m, m, m)
            content.append(new_string)

    if testMode > 2:
        # Generate STRAM array
        for m in range(num_features):
            for n in range(num_classes):
                new_string = "Xsyn{}{} pre{} post{} mon{}{} STRAM \n".format(m, n, m, n, m, n)
                content.append(new_string)
                new_string = "XB{}{} testpre{} testpost{} mon{}{} train BStore \n".format(m, n, m, n, m, n)
                content.append(new_string)

    if testMode > 3:
        for n in range(num_classes):
            new_string = "Xbda{} post{} vnin{} vnout{} l{} BDA \n".format(n, n, n, n, n)
            content.append(new_string)

    if testMode > 4:
        for n in range(num_classes):
            new_string = "Xno{} vnin{} vnout{} liaf \n".format(n, n, n)
            content.append(new_string)


    Ckt_element_fn = "DigitFiles/GeneratedCkt.sp"
    SpiceWriter(content, Ckt_element_fn)


if __name__ == "__main__":
    main()

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

- Row Node Layer
(Xr0 - Xrm)
in = niout0-nioutm
pre = pre0 -prem
dec = d0 - dm
train = train
clk = clk

- STRAM array
pre = pre0 - prem
post = post0 - postn
mon = mon00 = monmn

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

# Thresholded Transfer of Weights
TIA - Thresholded Transimpedance Amplifier: XTIA0 - XTIAn
post - iout0 - ioutn (column-wise)
thresh - thresh0 - threshn (col-wise)

- Bstore Row Control: XBR0-XBRm
in = niout0-nioutm
pre = tpre0 - tprem
train = train
reset = reset
clk = clkBM
dec = d0 - dm
bclk = bclk0 - bclkm

- mxn BStore Array: XB00 - XBmn
Bstore: pre, post, thresh, dec, reset, clk, mon
pre = pre0 - prem
post = tpost0 - tpostn
thresh = thresh0 - threshn (col-wise)
dec = d0 - dm (row-wise)
reset = reset
clk = bclk0 - bclkm
mon = bmon00 - bmonmn


"""

def architecture(breakDev):

    content = []
    if breakDev:
        num_bits = 20
    else:
        num_bits = 0
    num_features = 35
    num_classes = 3

    testMode = 8

    # I can totally make this in one double loop. Just for now, I want to build it
    #up

    # Generate the input neuron layer:
    for m in range(num_features):
        new_string = "Xni{} vi{} niout{} liaf \n".format(m, m, m)
        content.append(new_string)

    if testMode > 1:
        # Generate Row Node Layer
        for m in range(num_features):
                new_string = "Xr{} niout{} pre{} d{} train clk rowNode \n".format(m, m, m, m)
                content.append(new_string)

    if testMode > 2:
        # Generate STRAM Array
        device_num = np.random.choice(num_features * num_classes, num_bits, replace=False)
        print(device_num)
        counter = 0
        for m in range(num_features):
            for n in range(num_classes):
                if counter in device_num:
                    dev = "STRAM_broke"
                else:
                    dev = "STRAM"

                new_string = "Xsyn{}{} pre{} post{} mon{}{} {} \n".format(m, n, m, n, m, n, dev)
                content.append(new_string)
                counter += 1

    if testMode > 3:
        # Generate BDA array
        for n in range(num_classes):
            new_string = "Xbda{} post{} vnin{} vnout{} vl{} BDA \n".format(n, n, n, n, n)
            content.append(new_string)

    if testMode > 4:
        # Generate Neuron Layer
        for n in range(num_classes):
            new_string = "Xno{} vnin{} vnout{} liaf \n".format(n, n, n)
            content.append(new_string)

    if testMode > 5:
        # Generate TIAs
        for n in range(num_classes):
            new_string = "Xtia{} post{} thresh{} tiamon{} tia \n".format(n, n, n, n)
            content.append(new_string)

    if testMode > 6:
        # Generate Binary Memory Layer
        for m in range(num_features):
            new_string = "XBR{} niout{} tpre{} train reset clkBM d{} bclk{} BRowNode \n".format(m, m, m, m, m)
            content.append(new_string)

    if testMode > 7:
        # Generate Binary Memory Layer
        for m in range(num_features):
            for n in range(num_classes):
                new_string = "XB{}{} tpre{} tpost{} thresh{} d{} reset bclk{} bmon{}{} bstore \n".format(m, n, m, n, n, m, m, m, n)
                content.append(new_string)


    Ckt_element_fn = "DigitFiles/architecture{}.sp".format(num_bits)
    SpiceWriter(content, Ckt_element_fn)

def decoder(n):
    # Return the content for up to a 63bit decoder

    content = []
    for i in range(n):
        index = "{:06b}".format(i)
        print(index)
        s = "X{} ".format(i)
        for j, bit in enumerate(index[::-1]):
            if int(bit) == 1:
                append = "in{} ".format(j)
            else:
                append = "iin{} ".format(j)
            s = s + append
        print(s)
        s = s + "d{} and6\n".format(i)
        content.append(s)
    Ckt_element_fn = "DigitFiles/Decoder.sp"
    SpiceWriter(content, Ckt_element_fn)

def dmux(n):
    # Return the content for up to a 63bit decoder
    content = []
    for i in range(n):
        s = "X{} d{} in r{} and\n".format(i, i, i)
        print(s)
        content.append(s)
    Ckt_element_fn = "DigitFiles/DMUX.sp"
    SpiceWriter(content, Ckt_element_fn)

def genClks(s, time, Ton, delay, ramp, num_features, mode):
    if not mode:
        #s = s + "time 0 time+ramp vdd time+ramp+Ton vdd time+2*ramp+Ton 0"
        time = time+Ton+2*ramp
    for i in range(num_features):
        s = s + "{} 0 {} vdd {} vdd {} 0 ".format(time, time+ramp, time+ramp+Ton, time+2*ramp+Ton)
        time = time + delay
    return s



def clkSigs():
    content = []
    train_start=91e-3
    num_features=35
    Ton, delay = 5e-9, 20e-6
    ramp = 1e-11
    s = "vdecclk clk 0 PWL(0 0 2n 0 2.01n vdd 10n vdd 10.01n 0 "
    content.append(genClks(s, train_start, Ton, delay, ramp, num_features, 0)+")\n")
    s = "vdffclk clkBM 0 PWL(0 0 2n 0 2.01n vdd 10n vdd 10.01n 0 "
    content.append(genClks(s, train_start, Ton, delay, ramp, num_features, 1)+")\n")
    content.append("vr reset 0 PWL(0 0 5n 0 5.01n vdd)")
    Ckt_element_fn = "DigitFiles/clks.sp"
    SpiceWriter(content, Ckt_element_fn)


if __name__ == "__main__":
    #dmux(35)
    #decoder(35)
    #architecture(True)
    clkSigs()

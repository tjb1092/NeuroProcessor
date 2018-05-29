import numpy as np


#Infinite Gain- Multi-Feedback Bandpass Filter w/ Gain defined
#Gain heurisically found separately.
def DesignFilterBank():
    fl = np.array([1200., 1500., 2500., 2700., 2900., 3200., 4800., 4100.])
    fh = np.array([1500., 1800., 2700., 2800., 3100., 3500., 5200., 4600.])

    fc = np.sqrt(np.multiply(fl,fh))
    print("fc:")
    print(fc)

    BW = np.subtract(fh,fl)
    print("BW:")
    print(BW)
    Q = np.divide(fc,BW)
    print("Q:")
    print(Q)
    K = 3.2;

    R1n = np.divide(Q,K)
    print("R1n:")
    print(R1n)
    R2n = np.multiply(Q,2)
    print("R2n:")
    print(R2n)
    R3n = np.divide(Q, np.subtract(np.multiply(2, np.square(Q)),K))
    print("R3n:")
    print(R3n)

    ISF = 10000.0
    FSF = np.multiply(2. * np.pi, fc)

    C = np.divide(1., ISF * FSF)
    R1 = ISF * R1n
    R2 = ISF * R2n
    R3 = ISF * R3n
    print("C:")
    print(C)
    print("R1:")
    print(R1)
    print("R2:")
    print(R2)
    print("R3:")
    print(R3)
    return R1, R2, R3, C, C

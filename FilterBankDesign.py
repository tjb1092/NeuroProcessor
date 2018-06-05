import numpy as np


#Infinite Gain- Multi-Feedback Bandpass Filter w/ Gain defined
#Gain heurisically found separately.
def DesignFilterBank():
    fl = np.array([80., 100., 300., 400., 600., 1000., 2200., 4000.])
    fh = np.array([150., 300., 400., 600., 900., 1500., 2500., 5000.])

    fc = np.sqrt(np.multiply(fl,fh))
    print("fc: {}".format(fc))

    BW = np.subtract(fh,fl)
    print("BW: {}".format(BW))
    Q = np.divide(fc,BW)
    print("Q: {}".format(Q))
    K = 3.2;

    R1n = np.divide(Q,K)
    print("R1n: {}".format(R1n))
    R2n = np.multiply(Q,2)
    print("R2n: {}".format(R2n))
    R3n = np.divide(Q, np.subtract(np.multiply(2, np.square(Q)),K))
    print("R3n: {}".format(R3n))

    ISF = 10000.0
    FSF = np.multiply(2. * np.pi, fc)
    print("FSF: {}".format(FSF))

    C = np.divide(1., ISF * FSF)
    R1 = ISF * R1n
    R2 = ISF * R2n
    R3 = ISF * R3n
    print("C: {}".format(C))
    print("R1: {}".format(R1))
    print("R2: {}".format(R2))
    print("R3: {}".format(R3))
    return R1, R2, R3, C, C

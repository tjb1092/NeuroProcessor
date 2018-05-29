import matplotlib.pyplot as plt
from scipy.fftpack import fft
from scipy.io import wavfile
from utils import getV
import numpy as np
import seaborn as sns; sns.set(color_codes = True)
import math


def FFT_plot(filenames):
    decible_lst = []
    sample_rate = 11025
    for i in range(len(filenames)):
        decible = FFT_analysis(filenames[i])
        decible = decible[0:math.floor(sample_rate/2)]
        decible_lst.append(decible)
        #plt.semilogx(decible)

    mean = np.empty([1,math.floor(sample_rate/2)])
    variance = np.empty([1,math.floor(sample_rate/2)])
    n = len(decible_lst)
    #plt.show()
    # Simple Mean calculator
    for i in range(math.floor(sample_rate/2)):
        summer = 0
        for j in range(n):
            summer += decible_lst[j][i]
        mean[0][i] = summer/n
    print("Mean response calculated...")
    #plt.semilogx(mean[0][:])

    for i in range(math.floor(sample_rate/2)):
        summer = 0
        for j in range(n):
            summer += (decible_lst[j][i] - mean[0][i])**2
        variance[0][i] = summer/n
    print("Variance calculated...")
    plt.semilogx(variance[0][:])
    plt.grid(True, which="both", color='k')
    plt.xlabel("Frequency")
    plt.ylabel("Variance Magnitude")
    plt.title("Variance Analysis")
    plt.show()


def FFT_analysis(filename):
    fs, data = wavfile.read(filename)
    a = data.T[0] #This is a two channel soundtrack? Take first one.
    b=[(ele/2**16.)*2 for ele in a] # this is 16-bit track, b is now normalized on [-1,1)
    c = fft(b) # calculate fourier transform (complex numbers list)
    d = int(len(c)/2)  # you only need half of the fft list (real signal symmetry)

    return (np.log10(abs(c[:(d-1)]))*20)

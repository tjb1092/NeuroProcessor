import matplotlib.pyplot as plt
from scipy.fftpack import fft
from scipy.io import wavfile
from utils import getV
import numpy as np
import seaborn as sns; sns.set(color_codes = True)
import math
import os

def FFT_plot(filenames):

    #This doesn't work anymore
    decible_lst = []
    freq_lst = []
    sample_rate = 11025
    for i in range(len(filenames)):
        freq, decible = FFT_analysis(filenames[i])

        #decible = decible[0:math.floor(sample_rate/2)]
        decible_lst.append(decible)
        freq_lst.append(freq)
        #plt.semilogx(decible)

    mean = np.empty([1,len(decible_lst[0])])
    variance = mean
    n = len(decible_lst)
    #plt.show()
    # Simple Mean calculator
    for i in range(len(decible_lst[0])-1):
        summer = 0
        for j in range(n):
            summer += decible_lst[j][i]
        mean[0][i] = summer/n
    print("Mean response calculated...")
    #plt.semilogx(mean[0][:])

    for i in range(len(decible_lst[0])-1):
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
    N = len(b)
    win = np.hamming(N)
    x = b[0:N] * win
    sp = np.fft.rfft(x)
    mag = np.abs(sp)
    ref = np.sum(win)/2
    s_dbfs = 20* np.log10(mag/ref)
    freq = np.arange((N/2) + 1) / (float(N)/ fs)
    return freq, s_dbfs


def filter_Ranges(Rlist, freq, printInfo):
    #Rlist has tuples that are indicies for the freq array.
    tensThresh = 30
    hundredsThresh = 100
    thousandsThresh = 400
    thresh = 0 #init variable
    itemLst = []

    for item in Rlist:
        if freq[item[0]] < 100 or freq[item[1]] < 100:
            #can have ranges of about 30Hz min
            thresh = tensThresh
        elif freq[item[0]] < 1000 or freq[item[1]] < 1000:
            #Can have ranges of probably 100-200Hz min
            thresh = hundredsThresh
        else:
            #In the kHz regime, probably 400-500Hz range min
            thresh = thousandsThresh

        if printInfo:
            print(thresh)
            print(freq[item[1]]-freq[item[0]])
        if (freq[item[1]]-freq[item[0]]) < thresh:
            if printInfo:
                print("deleting: {} or {} to {}".format(item, freq[item[0]], freq[item[1]]))
            itemLst.append(item)

    # Has to be done outside of that loop b/c it messes with the iterator count
    for item in itemLst:
        Rlist.remove(item)

    return Rlist

def round_down(num, divisor):
    return num - (num%divisor)


def FFT_Ranges():
    #Flags and parameters
    pltFlag = True
    printInfo = False #flag for more info
    sample_rate = 11025
    dir_path = os.path.dirname(os.path.realpath(__file__))
    AudioFolder = os.path.join(dir_path, 'FullAudio')
    AudioLst = []

    #Step 1: get a list of each person to be tested. This should be abstracted at this point
    for x in os.walk(AudioFolder):
        if x[0] != AudioFolder:
            V = x[0].replace(AudioFolder,"")[1:]
            if (not(V == "NormalizationTest" or V == "Tony")):
                vfile = os.path.join(x[0], V+"_Normalized_NoiseReduced.wav")
                AudioLst.append(vfile)

    #Step 2: get fft's of each person
    smoothedAudioLst = []
    freq_lst = []
    maxFreq = [0]  # Find longest freq array
    for audio in AudioLst:
        freq, data = FFT_analysis(audio)
        smoothed = data

        #Smooth the data.
        avg_num = 20
        for i in range(avg_num,len(data)+avg_num):
            smoothed[i-avg_num] = np.average(data[i-avg_num:i])

        smoothedAudioLst.append(smoothed)
        freq_lst.append(freq) # need this to properly plot this
        if len(freq) > len(maxFreq):
            maxFreq = freq

    # Interpolate each one so that they have a relatable len
    modSpeclst = []
    index = 0
    for freq in freq_lst:
        yinterp = np.interp(maxFreq,freq,smoothedAudioLst[index])
        modSpeclst.append(yinterp)
        index += 1

    #Keep list of all winning ranges for each person
    winningCombos = []
    AllWinningCombos = []

    # Go through each combination and figure out where each person wins
    for V1 in range(len(modSpeclst)):
        for V2 in range(V1+1,len(modSpeclst)):
            #v1 and v1 should be indicies for smoothedAudioLst

            V1_lst = []
            V2_lst = []
            audioV1 = modSpeclst[V1]
            audioV2 = modSpeclst[V2]
            if pltFlag:
                plt.semilogx(maxFreq, audioV1)
                plt.semilogx(maxFreq, audioV2)
                plt.show()
            if audioV1[0] > audioV2[0]:
                isV1 = True
            else:
                isV1 = False
            Vstart = 0

            for i in range(len(modSpeclst[V1])):
                if isV1 and audioV1[i] < audioV2[i]:
                    # On V1, but V2 now overtook. Switch and log entry
                    V1_lst.append((Vstart,i)) #log V2 from previous start to now
                    Vstart = i #restart Vstart to current iteration
                    isV1 = False
                elif not isV1 and audioV1[i] >= audioV2[i]:
                    # On V2, but V1 now overtook. Switch and log entry
                    V2_lst.append((Vstart,i)) #log V2 from previous start to now
                    Vstart = i #restart Vstart to current iteration
                    isV1 = True

            #After loop, store last entry with final datapoint.
            if isV1:
                V1_lst.append((Vstart,i))
            else:
                V2_lst.append((Vstart,i))

            """
            print("pre filtering")

            print("V1's ranges:\n {}\n".format(AudioLst[V1]))
            for item in V1_lst:
                print(item)
                print("{:0.1f}, {:0.1f}".format(maxFreq[item[0]], maxFreq[item[1]]))

            print("V2's ranges\n {}\n".format(AudioLst[V2]))
            for item in V2_lst:
                print(item)
                print("{:0.1f}, {:0.1f}".format(maxFreq[item[0]], maxFreq[item[1]]))
            """

            V1_lst = filter_Ranges(V1_lst,maxFreq, printInfo)
            V2_lst = filter_Ranges(V2_lst,maxFreq, printInfo)


            v1_freqRanges = []

            if printInfo:
                print("post filtering")
                print("V1's ranges:\n {}\n".format(AudioLst[V1]))
            for item in V1_lst:
                Frange = (maxFreq[item[0]],maxFreq[item[1]])
                if Frange[0] and Frange[1]:
                    v1_freqRanges.append(Frange) #Only append non-empty tuples
                    AllWinningCombos.append(Frange)
                if printInfo:
                    print("({:0.1f}, {:0.1f})".format(Frange[0], Frange[1]))
            v2_freqRanges = []
            if printInfo:
                print("V2's ranges\n {}\n".format(AudioLst[V2]))
            for item in V2_lst:
                Frange = (maxFreq[item[0]],maxFreq[item[1]])
                if Frange[0] and Frange[1]:
                    v2_freqRanges.append(Frange) #Only append non-empty tuples
                    AllWinningCombos.append(Frange)
                if printInfo:
                    print("({:0.1f}, {:0.1f})".format(Frange[0], Frange[1]))

            #Store all of this info
            winningCombos.append({AudioLst[V1]:v1_freqRanges, AudioLst[V2]:v2_freqRanges})

    # Do some heuristic rounding to make the ranges line up a bit better visually
    AllWinningCombos.sort(key=lambda tup: tup[1])
    roundedCombos = []
    for i in AllWinningCombos:

        if i[0] < 100:
            divisor = 10.
        elif i[0] < 1000:
            divisor = 50.
        else:
            divisor = 500.

        roundedCombos.append((round_down(i[0], divisor), round_down(i[1], divisor)))

    for i in roundedCombos:
        print("({}, {})".format(int(i[0]),int(i[1])))

    #Now we have all of the combos, we need a way to pick ranges from this info.

    selectedRanges = [(70,150), (300,450), (400,600), (700,800), (1000, 2000), (2500, 3000), (4000, 5000)]

    #Did it manually for now. Now, I have to check for each pairing, does each person fit into a range that allows them to win.
    #For now, I'm manually checking till I can figure out an algorithmic way of doing this
    for pair in winningCombos:
        for key in pair:
            print(key[62:-28])
            for Arange in pair[key]:
                print("({:0.1f},{:0.1f})".format(Arange[0],Arange[1]))

        print("\n")


FFT_Ranges()

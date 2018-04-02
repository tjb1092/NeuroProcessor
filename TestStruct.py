import sys
import os
from pydub import AudioSegment
from random import shuffle, sample
import math
import pickle
from utils import getV, printSuccess, dataPickle, genVTest, genVTrain

def MultiV(v1, v2, audio, Train_Test_Split,Train_Mode,Test_Mode):

    # Get list of V1 files & create list data structure
    V1, V1_trainLen, V1_testLen = getV(v1, audio, Train_Test_Split, 1)

    # Get list of V2 files & create list data structure
    V2, V2_trainLen, V2_testLen = getV(v2, audio, Train_Test_Split, 2)

    # Create V_Test Wav file
    if Train_Mode == 1:
        # Cheeky little index alternator
        V1_index = 0
        V2_index = 0
        V_train = []
        #Note this won't work for % based splits b/c its only one value
        for index in range(int(Train_Test_Split[0])):
            if index%2 == 0:
                V_train.append(V1[V1_index])
                V1_index += 1
            else:
                V_train.append(V2[V2_index])
                V2_index += 1
    else:
        # Random for corner case.
        # Create V_Train Wav file
        V_train = V1[0:V1_trainLen] + V2[0:V2_trainLen]
        shuffle(V_train)

    silence = genVTrain(V_train)

    if Test_Mode == 1:

        if Train_Mode != 1:
            # If the mode is 1, then the indicies already exist and
            #have the correct value.
            V1_index = V1_trainLen
            V2_index = V2_trainLen

        # Cheeky little index alternator
        V_test = []
        #Note this won't work for % based splits b/c its only one value
        for index in range(int(Train_Test_Split[1])):
            if index%2 == 0:
                V_test.append(V1[V1_index])
                V1_index += 1
            else:
                V_test.append(V2[V2_index])
                V2_index += 1
    else:
        # Random for the corner case.
        # I will linearly index from here b/c the samples are randomized already.
        V_test= V1[V1_trainLen:V1_trainLen+V1_testLen] + V2[V2_trainLen:V2_trainLen+V2_testLen]
        shuffle(V_test)

    genVTest(V_test, silence)

    data = dataPickle(V_train, V_test, len(audio)+1)
    printSuccess()
    return data

def SingleV(v1, audio, Train_Test_Split):
    # Get list of V1 files & create list data structure
    V1, V1_trainLen, V1_testLen = getV(v1, audio, Train_Test_Split, 1)
    # Create V_Train Wav file
    V_train = V1[0:V1_trainLen]
    shuffle(V_train)
    silence = genVTrain(V_train)

    # Create V_Test Wav file
    V_test= V1[V1_trainLen:V1_trainLen+V1_testLen]
    shuffle(V_test)
    genVTest(V_test, silence)

    data = dataPickle(V_train, V_test, len(audio)+1)
    printSuccess()
    return data

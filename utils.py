import sys
import os
from pydub import AudioSegment
from random import shuffle, sample
import math
import pickle
from FindVoiceTiming import voiceTimings
from SpiceModifier import GenerateLabels


def getV(v, audio, Train_Test_Split, label):
    # Get list of V files & create list data structure

    # Iterate through each file set in the walk and get a list of all of the audio files
    V = []
    for dirpath, dirs, files in os.walk(os.path.join(audio, v)):
        for afile in files:
            V.append((os.path.join(audio,v,afile), label)) # Make the file a tuple to have a label

    shuffle(V) # Randomize list order

    if type(Train_Test_Split) is float:
        V_trainLen = math.ceil(len(V) * Train_Test_Split)
        V_testLen = len(V) - V_trainLen
    elif type(Train_Test_Split) is list:
        #Split half data for V1 and half for V2. I relize this is pretty dumb for the 1 voice option
        #We do what we must because we can.
        V_trainLen = math.ceil(float(Train_Test_Split[0])/2.0)
        V_testLen = math.ceil(float(Train_Test_Split[1])/2.0)
    return V, V_trainLen, V_testLen


def printSuccess():
    Success = """
       _____                             _
      / ____|                           | |
     | (___  _   _  ___ ___ ___  ___ ___| |
      \___ \| | | |/ __/ __/ _ \/ __/ __| |
      ____) | |_| | (_| (_|  __/\__ \__ \_|
     |_____/ \__,_|\___\___\___||___/___(_)
    """
    print(Success)


def dataPickle(V_train, V_test, folderName, index):
    # Store data into pickle file for later if needed.
    for i in range(len(V_train)):
        V_train[i] = (V_train[i][0][index:-4])

    for i in range(len(V_test)):
        V_test[i] = (V_test[i][0][index:-4])

    data = {"Train": V_train, "Test": V_test}
    pickle.dump( data, open( os.path.join('.', "SimInput", folderName, "data_info.p"), "wb" ) )
    return data


def genVTest(V_test, silence,folderName):
    ############################################################################
    # Create V_Test Wav file


    # Dummy one to instantiate object. Maybe it can be constructed w/o an input,
    # but I don't think it is likely without changing the code.
    V_Test_Wav = AudioSegment.from_wav(V_test[0][0])

    for clip in V_test[1:len(V_test)]:
        sound = AudioSegment.from_wav(clip[0])  # Index into the tuple to  get the filename

        V_Test_Wav = V_Test_Wav + sound

    print("V_test duration w/o silence")
    print(V_Test_Wav.duration_seconds)

    V_Test_Wav = silence + V_Test_Wav
    print("V_test duration w/ silence")
    print(V_Test_Wav.duration_seconds)

    print("Len of VTest:")
    print(len(V_test))

    # Export The Wav file
    V_Test_Wav.export(os.path.join('.', "SimInput", folderName, "V_test.wav"), format="wav")




def genVTrain(V_train,folderName):

    #Init output label info.
    total_duration = 0.0
    outputPattern = [[0.0,0]] # Start "off"

    """
    For each audio file:
    assume it is 0V beforehand.
    start:
    voice start:
    total_duration + v_start
    total_duration + v_start+ 0.01

    voice end:
    total_duration + v_end
    total_duration + v_end+ 0.01

    end:
    new_total_duration
    """

    # Dummy one to instantiate object. Maybe it can be constructed w/o an input,
    # but I don't think it is likely without changing the code.
    Timings = voiceTimings(V_train[0][0])  # Analyze voice data to find start (0) and end (1) timing

    V_Train_Wav = AudioSegment.from_wav(V_train[0][0])

    outputPattern.append([total_duration+Timings[0], 0])  # Voice starts
    outputPattern.append([total_duration+Timings[0]+.01, V_train[0][1]])  # Add +0.01 to that you get an effective step function.

    outputPattern.append([total_duration+Timings[1], V_train[0][1]])  # Voice ends
    outputPattern.append([total_duration+Timings[1]+.01, 0])  # Add +0.01 to that you get an effective step function.

    # Find duration of audio sample. make end a 0 to ensure next sample start 0.
    total_duration += V_Train_Wav.duration_seconds
    outputPattern.append([total_duration, 0])

    for clip in V_train[1:len(V_train)]:
        Timings = voiceTimings(clip[0])  # Analyze voice data to find start (0) and end (1) timing
        sound = AudioSegment.from_wav(clip[0])  # Index into the tuple to  get the filename

        outputPattern.append([total_duration+Timings[0], 0])  # Voice starts
        outputPattern.append([total_duration+Timings[0]+.01, clip[1]])  # Add +0.01 to that you get an effective step function.

        outputPattern.append([total_duration+Timings[1], clip[1]])  # Voice ends
        outputPattern.append([total_duration+Timings[1]+.01, 0])  # Add +0.01 to that you get an effective step function.

        # Find duration of audio sample. make end a 0 to ensure next sample start 0.
        total_duration += sound.duration_seconds
        outputPattern.append([total_duration, 0])

        V_Train_Wav = V_Train_Wav + sound

    outputPattern.append([total_duration+.01, 0])  # Turn labels off after signal passes through.
    print("V_train duration:" )
    print(V_Train_Wav.duration_seconds)

    print("Len of VTrain:")
    print(len(V_train))

    # Generate Output Labels
    GenerateLabels(outputPattern, folderName)


    silence = V_Train_Wav - 100  # Creates hopefully a file that is basically silent. -100dB might be overkill

    # Export The Wav files
    V_Train_Wav.export(os.path.join('.', "SimInput", folderName, "V_train.wav"), format="wav")
    return silence


def GetUserInput(Text):
    print(Text)

    InputChecker = False

    while(not(InputChecker)):
        choice = int(input("Your Selection: \n"))

        # Kinda a bad cop-out for now. should work in 7/9 cases currently. Good enough.
        # Upgrade would be an expansive if statement based on how many choices correspond to each text option.
        if choice == 1 or choice == 2 or choice == 3 or choice == 4 or choice == 5:
            InputChecker = True
        else:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(Text)
            print("Please enter a valid option.")

    return choice

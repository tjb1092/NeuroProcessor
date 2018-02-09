import sys
import os
from pydub import AudioSegment
from random import shuffle, sample
import math
import pickle
from SpiceModifier import GenerateLabels
from FindVoiceTiming import voiceTimings
def Random_Random(v1, v2, audio):
    Train_Split_Percent = 0.8

    ############################################################################
    # Get list of V1 files & create list data structure

    # Iterate through each file set in the walk and get a list of all of the audio files
    V1 = []
    for dirpath, dirs, files in os.walk(os.path.join(audio, v1)):
        for afile in files:
            V1.append((os.path.join(audio,v1,afile), 1)) # Make the file a tuple to have a label

    shuffle(V1) # Randomize list order

    V1_trainLen = math.ceil(len(V1) * Train_Split_Percent)
    V1_testLen = len(V1) - V1_trainLen

    ############################################################################
    # Get list of V2 files & create list data structure

    # Iterate through each file set in the walk and get a list of all of the audio files
    V2 = []
    for dirpath, dirs, files in os.walk(os.path.join(audio, v2)):
        for afile in files:
            V2.append((os.path.join(audio,v2,afile), 2))

    shuffle(V2) # Randomize list order

    # Figure out the trian/test split.
    V2_trainLen = math.ceil(len(V2) * Train_Split_Percent)
    V2_testLen = len(V2) - V2_trainLen

    ############################################################################
    # Create V_Train Wav file


    # I will linearly index from here b/c the samples are randomized already.
    V_train = V1[0:V1_trainLen] + V2[0:V2_trainLen]
    shuffle(V_train) # Shuffle the two files together

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

    input("pause")

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
    GenerateLabels(outputPattern)


    silence = V_Train_Wav - 100  # Creates hopefully a file that is basically silent. -100dB might be overkill


    ############################################################################
    # Create V_Test Wav file

    # I will linearly index from here b/c the samples are randomized already.
    V_test= V1[V1_trainLen:V1_trainLen+V1_testLen] + V2[V2_trainLen:V2_trainLen+V2_testLen]
    shuffle(V_test) # Shuffle the two files together

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


    # Export The Wav files

    V_Train_Wav.export(os.path.join('.', "V_train.wav"), format="wav")

    V_Test_Wav.export(os.path.join('.', "V_test.wav"), format="wav")

    data = {"Train": V_train, "Test": V_test}
    pickle.dump( data, open( os.path.join('.', "SimInput", "data_info.p"), "wb" ) )
    Success = """
       _____                             _
      / ____|                           | |
     | (___  _   _  ___ ___ ___  ___ ___| |
      \___ \| | | |/ __/ __/ _ \/ __/ __| |
      ____) | |_| | (_| (_|  __/\__ \__ \_|
     |_____/ \__,_|\___\___\___||___/___(_)
    """
    print(Success)
    return data


def main():

    Title = """
                        _ _          _____                           _
         /\            | (_)        / ____|                         | |
        /  \  _   _  __| |_  ___   | |  __  ___ _ __   ___ _ __ __ _| |_ ___  _ __
       / /\ \| | | |/ _` | |/ _ \  | | |_ |/ _ \ '_ \ / _ \ '__/ _` | __/ _ \| '__|
      / ____ \ |_| | (_| | | (_) | | |__| |  __/ | | |  __/ | | (_| | || (_) | |
     /_/    \_\__,_|\__,_|_|\___/   \_____|\___|_| |_|\___|_|  \__,_|\__\___/|_|


    Enter a Train/Test configuration:
    (1) Random / Random
    (2) Segments / Random (In Development)
    (3) Segments / Segments (In Development)
    """
    print(Title)

    InputChecker = False

    while(not(InputChecker)):
        mode = int(input("Your Selection: \n"))

        if mode == 1 or mode == 2 or mode == 3:
            InputChecker = True
        else:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(Title)
            print("Please enter a valid option.")


    dir_path = os.path.dirname(os.path.realpath(__file__))
    AudioFolder = os.path.join(dir_path, 'Audio')

    print("Available Audio Data Folder Names:")
    for x in os.walk(AudioFolder):
        if x[0] != AudioFolder:
            print(x[0].replace(AudioFolder,""))

    print("Please pick the two voices you would like to differentiate:")

    V1 = input("Voice 1: ")
    V2 = input("Voice 2: ")

    if mode == 1:
        Random_Random(V1,V2, AudioFolder)

    elif mode == 2:
        print("hi")
    elif mode == 3:
        print("hi")

main()

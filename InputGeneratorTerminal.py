import sys
import os
from pydub import AudioSegment
from random import shuffle, sample
import math
import pickle
from TestStruct import MultiV, SingleV
from utils import GetUserInput
from SamplePatterns import samplePattern
from FFT_Analysis import FFT_plot
from SpiceModifier import GenerateFilterBank

def main():

    Title = """
                    _ _          _____                           _
     /\            | (_)        / ____|                         | |
    /  \  _   _  __| |_  ___   | |  __  ___ _ __   ___ _ __ __ _| |_ ___  _ __
   / /\ \| | | |/ _` | |/ _ \  | | |_ |/ _ \ '_ \ / _ \ '__/ _` | __/ _ \| '__|
  / ____ \ |_| | (_| | | (_) | | |__| |  __/ | | |  __/ | | (_| | || (_) | |
 /_/    \_\__,_|\__,_|_|\___/   \_____|\___|_| |_|\___|_|  \__,_|\__\___/|_|


Enter a Train/Test configuration:
(1) Single Voice Randomized
(2) Random / Random
(3) Alternating / Random
(4) Alternating / Alternating

Extra Functionality:
(5) View a generated sequence order
(6) FFT analysis of audio
(7) Generate FilterBank.asc based on frequency ranges
    """

    mode = GetUserInput(Title)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    AudioFolder = os.path.join(dir_path, 'Audio')
    if mode == 5:

        DataFolder = os.path.join(dir_path, 'SimInput')
        print("Available Data Series: ")
        for x in os.walk(DataFolder):
            if x[0] != DataFolder:
                print(x[0].replace(DataFolder,"")[1:])

        V_file = input("Choose a name: ")
        samplePattern(V_file)
    elif mode == 6:
        typeDialog ="""
Permute over all voice pairs?:
(1) Yes
(2) No
        """
        isPermute = GetUserInput(typeDialog)
        FullAudioFolder = os.path.join(dir_path,"FullAudio")
        if(isPermute == 1):
            #Doing this second
            AudioLst = []
            for x in os.walk(FullAudioFolder):
                if x[0] != FullAudioFolder:
                    V = x[0].replace(FullAudioFolder, "")[1:]
                    if (not(V == "NormalizationTest" or V == "Tony")):

                        vfile = os.path.join(x[0], V+"_Normalized_NoiseReduced.wav")
                        AudioLst.append(vfile)
            FFT_plot(AudioLst)
        else:
            # Manually pick the voices
            print("Available Audio Data Folder Names:")
            for x in os.walk(AudioFolder):
                if x[0] != AudioFolder:
                    print(x[0].replace(AudioFolder,"")[1:])

            print("Please pick the voice you would like to take the FFT of:")

            V = input("Voice: ")
            vfile = os.path.join(dir_path,"FullAudio", V, V+"_Normalized_NoiseReduced.wav")
            print(vfile)
            FFT_plot(vfile)
    elif mode == 7:
        GenerateFilterBank()

    else:

        typeDialog ="""
Train-Test-Split Type:
(1) X/100-X \% split Train/Test
(2) X/Y samples Train/Test
        """
        TTStype = GetUserInput(typeDialog)

        #Note, not doing type checking on inputs here.
        if TTStype == 1:
            TTS = float(input("Please Enter X: \n"))
        elif TTStype == 2:
            X = input("Please enter X: \n")
            Y = input("Please enter Y: \n")
            TTS = [X,Y]
        typeDialog ="""
Permute over all voice pairs?:
(1) Yes
(2) No
        """
        isPermute = GetUserInput(typeDialog)

        if(isPermute == 1):
            # X/Y implementation a bit off, but it should be okay.
            if mode == 1:
                for x in os.walk(AudioFolder):
                    if x[0] != AudioFolder:
                        V1 = x[0].replace(AudioFolder, "")[1:]
                        SingleV(V1, AudioFolder, TTS)
            else:

                AudioLst = []
                for x in os.walk(AudioFolder):
                    if x[0] != AudioFolder:
                        AudioLst.append(x[0].replace(AudioFolder, "")[1:])  #Figure out how many voices there are

                # Go through each combination
                for V1 in range(len(AudioLst)):
                    for V2 in range(V1+1,len(AudioLst)):
                        print(V1)
                        print(V2)
                        print("\n")
                        if mode == 2:
                            MultiV(AudioLst[V1],AudioLst[V2], AudioFolder, TTS, 0,0)
                        elif mode == 3:
                            MultiV(AudioLst[V1],AudioLst[V2], AudioFolder, TTS, 1,0)
                        elif mode == 4:
                            MultiV(AudioLst[V1],AudioLst[V2], AudioFolder, TTS, 1,1)
        else:
            # Manually pick the voices
            print("Available Audio Data Folder Names:")
            for x in os.walk(AudioFolder):
                if x[0] != AudioFolder:
                    print(x[0].replace(AudioFolder,"")[1:])

            print("Please pick the voice(s) you would like to differentiate:")

            V1 = input("Voice 1: ")
            if mode != 1:
                V2 = input("Voice 2: ")

            if mode == 1:
                SingleV(V1, AudioFolder, TTS)
            elif mode == 2:
                MultiV(V1,V2, AudioFolder, TTS, 0,0)
            elif mode == 3:
                MultiV(V1, V2, AudioFolder, TTS, 1,0)
            elif mode == 4:
                MultiV(V1, V2, AudioFolder, TTS, 1,1)

main()

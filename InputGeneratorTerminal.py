import sys
import os
from pydub import AudioSegment
from random import shuffle, sample
import math
import pickle
from TestStruct import MultiV, SingleV
from utils import GetUserInput


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
    """

    mode = GetUserInput(Title)

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
    dir_path = os.path.dirname(os.path.realpath(__file__))
    AudioFolder = os.path.join(dir_path, 'Audio')

    print("Available Audio Data Folder Names:")
    for x in os.walk(AudioFolder):
        if x[0] != AudioFolder:
            print(x[0].replace(AudioFolder,""))

    print("Please pick the voice(s) you would like to differentiate:")

    V1 = input("Voice 1: ")
    if mode != 1:
        V2 = input("Voice 2: ")

    # X/Y implementation a bit off, but it should be okay.
    if mode == 1:
        SingleV(V1, AudioFolder, TTS)
    elif mode == 2:
        MultiV(V1,V2, AudioFolder, TTS, 0,0)
    elif mode == 3:
        MultiV(V1, V2, AudioFolder, TTS, 1,0)
    elif mode == 4:
        MultiV(V1, V2, AudioFolder, TTS, 1,1)
main()

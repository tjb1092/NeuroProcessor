from LTSpiceRaw_Reader import LTSpiceRawRead
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.gridspec as gridspec
import seaborn as sns; sns.set(color_codes = True)
import math
from utils import GetUserInput
import os
import subprocess
import pickle
from SPICE_Raw_UnicodeFix import fix_bytes

def DataLoader():

    subprocess.call(os.path.join('.', "rmFrames.sh"))

    choice = input("Load New Data? [y/n]: ")
    if choice == "y":
        print("Loading Raw Data")
        SPICE_Obj = LTSpiceRawRead('Net Array_Small.raw')
        print('SPICE Object Created')

        #Need time, audioin, neuronin, neuronin2, predict, predict2
        t = SPICE_Obj.get_trace('time')
        t = np.absolute(t.data)  # Weird thing going on w/ this and random negative numbers showing up.

        ####################################
        # Read in Part 2 data.
        #Obviously very verbose and can be looped through in future iterations.
        Data = {"t": t,
                "audioin": SPICE_Obj.get_trace('V(audioin)').data,
                "nIn1": SPICE_Obj.get_trace('V(nin1)').data,
                "nIn2": SPICE_Obj.get_trace('V(nin2)').data,
                "pred1": SPICE_Obj.get_trace('V(predict)').data,
                "pred2": SPICE_Obj.get_trace('V(predict2)').data,
                "W1_1": SPICE_Obj.get_trace('V(vmem1_1)').data,
                "W1_2": SPICE_Obj.get_trace('V(vmem1_2)').data,
                "W2_1": SPICE_Obj.get_trace('V(vmem2_1)').data,
                "W2_2": SPICE_Obj.get_trace('V(vmem2_2)').data,
                "W3_1": SPICE_Obj.get_trace('V(vmem3_1)').data,
                "W3_2": SPICE_Obj.get_trace('V(vmem3_2)').data,
                "W4_1": SPICE_Obj.get_trace('V(vmem4_1)').data,
                "W4_2": SPICE_Obj.get_trace('V(vmem4_2)').data,
                "W5_1": SPICE_Obj.get_trace('V(vmem5_1)').data,
                "W5_2": SPICE_Obj.get_trace('V(vmem5_2)').data,
                "W6_1": SPICE_Obj.get_trace('V(vmem6_1)').data,
                "W6_2": SPICE_Obj.get_trace('V(vmem6_2)').data,
                "W7_1": SPICE_Obj.get_trace('V(vmem7_1)').data,
                "W7_2": SPICE_Obj.get_trace('V(vmem7_2)').data,
                "W8_1": SPICE_Obj.get_trace('V(vmem8_1)').data,
                "W8_2": SPICE_Obj.get_trace('V(vmem8_2)').data}
    else:
        #Recall pickled data for a quicker "cached" load time.
        Data = pickle.load(open( os.path.join('.', "SimInput", "raw_data.p"), "rb" ) )

    return Data



# Save each frame in a file for stitching into a .gif and .mp4
def Save_Frame(i, Data, SkipFactor):

    Audio = np.concatenate((Data["audioin"][0:(i*SkipFactor)],np.zeros(len(Data["t"])-(i*SkipFactor))))
    in1 = np.concatenate((Data["nIn1"][0:(i*SkipFactor)],np.zeros(len(Data["t"])-(i*SkipFactor))))
    in2 = np.concatenate((Data["nIn2"][0:(i*SkipFactor)],np.zeros(len(Data["t"])-(i*SkipFactor))))
    p1 = np.concatenate((Data["pred1"][0:(i*SkipFactor)],np.zeros(len(Data["t"])-(i*SkipFactor))))
    p2 = np.concatenate((Data["pred2"][0:(i*SkipFactor)],np.zeros(len(Data["t"])-(i*SkipFactor))))

    HM_Data = np.array([[Data["W1_1"][i*SkipFactor],Data["W1_2"][i*SkipFactor]],
                     [Data["W2_1"][i*SkipFactor],Data["W2_2"][i*SkipFactor]],
                     [Data["W3_1"][i*SkipFactor],Data["W3_2"][i*SkipFactor]],
                     [Data["W4_1"][i*SkipFactor],Data["W4_2"][i*SkipFactor]],
                     [Data["W5_1"][i*SkipFactor],Data["W5_2"][i*SkipFactor]],
                     [Data["W6_1"][i*SkipFactor],Data["W6_2"][i*SkipFactor]],
                     [Data["W7_1"][i*SkipFactor],Data["W7_2"][i*SkipFactor]],
                     [Data["W8_1"][i*SkipFactor],Data["W8_2"][i*SkipFactor]]])

    # plot it
    f, (a0, a1) = plt.subplots(1,2, gridspec_kw = {'width_ratios':[4, 1]})


    sns.heatmap(HM_Data, vmin=0, vmax=1.1, cmap=sns.cm.rocket_r, ax=a1)

    plt.setp(plt.getp(a1, 'xticklabels'), color='w')


    a0.set_xlim(( 0, 16.5))
    a0.set_ylim((-1, 11))
    a0.set_xlabel('Time (s)')
    a0.set_ylabel('Voltage (V)')

    a0.plot(Data["t"], Audio,  lw=2, label='Audio')
    a0.plot(Data["t"], in1,  lw=2, label='Post-Neuron 1 Input')
    a0.plot(Data["t"], in2,  lw=2, label='Post-Neuron 2 Input')
    a0.plot(Data["t"], p1,  lw=2, label='Prediction 1')
    a0.plot(Data["t"], p2,  lw=2, label='Prediction 2')

    a0.legend(loc='upper right')

    f.tight_layout()
    f.savefig('Frames/frame'+str(i)+'.png', dpi=300)

    plt.close(f)
    return


def CompleteGIF(SkipFactor):

    Data = DataLoader()
    Raw_DataPickle(Data)
    frame_num=math.ceil(len(Data["t"])/SkipFactor)
    for frame in range(1,frame_num):
        print ("Frame: " + str(frame) + "/ " + str(frame_num), end="\r")
        Save_Frame(frame, Data, SkipFactor)
    #Runs Bash script to make the video
    subprocess.call(os.path.join('.', "VidMaker.sh"))

def Raw_DataPickle(Data):
    # Store data into pickle file for later if needed.
    pickle.dump( Data, open( os.path.join('.', "SimInput", "raw_data.p"), "wb" ) )
    return

def main():
    """
    Sets the "resolution" of the animation.
    Determines how long the animations runs for and can be tuned to approx.
    "real-time" for demonstration purposes.
    """
    SkipFactor = 500


    Title = """
       _____                         _   _       __      ___                 _ _
      / ____|                       | | (_)      \ \    / (_)               | (_)
     | (___  _   _ _ __   __ _ _ __ | |_ _  ___   \ \  / / _ ___ _   _  __ _| |_ _______ _ __
      \___ \| | | | '_ \ / _` | '_ \| __| |/ __|   \ \/ / | / __| | | |/ _` | | |_  / _ \ '__|
      ____) | |_| | | | | (_| | |_) | |_| | (__     \  /  | \__ \ |_| | (_| | | |/ /  __/ |
     |_____/ \__, |_| |_|\__,_| .__/ \__|_|\___|     \/   |_|___/\__,_|\__,_|_|_/___\___|_|
              __/ |           | |
             |___/            |_|
    """

    os.system('cls' if os.name == 'nt' else 'clear')
    print(Title)
    fix_bytes("Net Array_Small.raw")
    CompleteGIF(SkipFactor)

main()

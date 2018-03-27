from LTSpiceRaw_Reader import LTSpiceRawRead
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation, rc
import seaborn as sns; sns.set(color_codes = True)
import math
from utils import GetUserInput
###############################33
# Some setup
SkipFactor = 1000

# equivalent to rcParams['animation.html'] = 'html5'
rc('animation', html='html5')

# First set up the figure, the axis, and the plot element we want to animate

#Gotta figure out how to globalize dis properly because it becomes a huge pain
fig, ax = plt.subplots()
ax.set_xlim(( 0, 16.5))
ax.set_ylim((-1, 11))

plot1, = ax.plot([], [], lw=2, label='Audio')
plot2, = ax.plot([], [], lw=2, label='Post-Neuron 1 Input')
plot3, = ax.plot([], [], lw=2, label='Post-Neuron 2 Input')
plot4, = ax.plot([], [], lw=2, label='Prediction 1')
plot5, = ax.plot([], [], lw=2, label='Prediction 2')
#HM = sns.heatmap(np.array(([0,0],[0,0])))

plt.xlabel('Time (s)')
plt.ylabel('Voltage (V)')
plt.legend(loc='upper right')


print("Loading Raw Data")
SPICE_Obj = LTSpiceRawRead('Net Array_Small.raw')
print('SPICE Object Created')

#Part 1, get the transient plots made

#Need time, audioin, neuronin, neuronin2, predict, predict2

t = SPICE_Obj.get_trace('time')
t = np.absolute(t.data)  # Weird thing going on w/ this and random negative numbers showing up.

#########
#The global depedencies of these things make it quite annoying to modularize it.
#I'll get to it if I can
audioin = SPICE_Obj.get_trace('V(audioin)').data
nIn1 = SPICE_Obj.get_trace('V(neuronin)').data
nIn2 = SPICE_Obj.get_trace('V(neuronin2)').data
pred1 = SPICE_Obj.get_trace('V(predict)').data
pred2 = SPICE_Obj.get_trace('V(predict2)').data
print('Transient Data Loaded')


####################################
# Read in Part 2 data

x_i = np.array(([1,2,6,10,15,21,17,24],[5,20,9,14,19,23,27,26]))

inout = SPICE_Obj.get_trace('V(inout)').data
inout2 = SPICE_Obj.get_trace('V(inout2)').data

#Yes this can be done in a loop, but I need to figure out how the data shapes work
pre1 = SPICE_Obj.get_trace('V(pre1)').data
pre2 = SPICE_Obj.get_trace('V(pre2)').data
pre3 = SPICE_Obj.get_trace('V(pre3)').data
pre4 = SPICE_Obj.get_trace('V(pre4)').data
pre5 = SPICE_Obj.get_trace('V(pre5)').data
pre6 = SPICE_Obj.get_trace('V(pre6)').data
pre7 = SPICE_Obj.get_trace('V(pre7)').data
pre8 = SPICE_Obj.get_trace('V(pre8)').data

#The numbering is also goofed up, so it is just complicated
i1 = SPICE_Obj.get_trace('Ix(x1:VPOST)').data
i2 = SPICE_Obj.get_trace('Ix(x2:VPOST)').data
i6 = SPICE_Obj.get_trace('Ix(x6:VPOST)').data
i10 = SPICE_Obj.get_trace('Ix(x10:VPOST)').data
i15 = SPICE_Obj.get_trace('Ix(x15:VPOST)').data
i21 = SPICE_Obj.get_trace('Ix(x21:VPOST)').data
i17 = SPICE_Obj.get_trace('Ix(x17:VPOST)').data
i24 = SPICE_Obj.get_trace('Ix(x24:VPOST)').data

i5 = SPICE_Obj.get_trace('Ix(x5:VPOST)').data
i6 = SPICE_Obj.get_trace('Ix(x6:VPOST)').data
i20 = SPICE_Obj.get_trace('Ix(x20:VPOST)').data
i9 = SPICE_Obj.get_trace('Ix(x9:VPOST)').data
i14 = SPICE_Obj.get_trace('Ix(x14:VPOST)').data
i19 = SPICE_Obj.get_trace('Ix(x19:VPOST)').data
i23 = SPICE_Obj.get_trace('Ix(x23:VPOST)').data
i27 = SPICE_Obj.get_trace('Ix(x27:VPOST)').data
i26 = SPICE_Obj.get_trace('Ix(x26:VPOST)').data

R1_1 = np.absolute((inout-pre1)/ i1)
R1_2 = np.absolute((inout2-pre1)/ i5)
R2_1 = np.absolute((inout-pre2)/ i2)
R2_2 = np.absolute((inout2-pre2)/ i20)
R3_1 = np.absolute((inout-pre3)/ i6)
R3_2 = np.absolute((inout2-pre3)/ i9)
R4_1 = np.absolute((inout-pre4)/ i10)
R4_2 = np.absolute((inout2-pre4)/ i14)
R5_1 = np.absolute((inout-pre5)/ i15)
R5_2 = np.absolute((inout2-pre5)/ i19)
R6_1 = np.absolute((inout-pre6)/ i21)
R6_2 = np.absolute((inout2-pre6)/ i23)
R7_1 = np.absolute((inout-pre7)/ i17)
R7_2 = np.absolute((inout2-pre7)/ i27)
R8_1 = np.absolute((inout-pre8)/ i24)
R8_2 = np.absolute((inout2-pre8)/ i26)
print('Heatmap Data Loaded')

# initialization function: plot the background of each frame
def init_heatmap():
    HM.set_data(np.array(([0,0],[0,0])))
    return (HM,)

# animation function. This is called sequentially
def animate_heatmap(i):
    print(i)
    Data = np.array(([R1_1[i],R2_1[i],R3_1[i],R4_1[i],R5_1[i],R6_1[i],R7_1[i],R8_1[i]],[R1_2[i],R1_2[i],R2_2[i],R3_2[i],R4_2[i],R5_2[i],R6_2[i],R7_2[i],R8_2[i]]))
    HM.set_data(Data)
    return (HM,)


# initialization function: plot the background of each frame
def init_transient():
    plot1.set_data([], [])
    plot2.set_data([], [])
    plot3.set_data([], [])
    plot4.set_data([], [])
    plot5.set_data([], [])
    return (plot1,plot2,plot3,plot4,plot5,)

# animation function. This is called sequentially
def animate_transient(i):
    print(i)
    Audio = np.concatenate((audioin[0:(i*SkipFactor)],np.zeros(len(t)-(i*SkipFactor))))
    in1 = np.concatenate((nIn1[0:(i*SkipFactor)],np.zeros(len(t)-(i*SkipFactor))))
    in2 = np.concatenate((nIn2[0:(i*SkipFactor)],np.zeros(len(t)-(i*SkipFactor))))
    p1 = np.concatenate((pred1[0:(i*SkipFactor)],np.zeros(len(t)-(i*SkipFactor))))
    p2 = np.concatenate((pred2[0:(i*SkipFactor)],np.zeros(len(t)-(i*SkipFactor))))

    plot1.set_data(t, Audio)
    plot2.set_data(t, in1)
    plot3.set_data(t, in2)
    plot4.set_data(t, p1)
    plot5.set_data(t, p2)

    return (plot1,plot2,plot3,plot4,plot5,)



def TransientGIF(t,SPICE_Obj, SkipFactor):


    # call the animator. blit=True means only re-draw the parts that
    # have changed.
    anim = animation.FuncAnimation(fig, animate_transient, init_func=init_transient,
                                   frames=math.ceil(len(t)/SkipFactor), interval=20, blit=True)
    anim.save('Transient_animation.gif', writer='imagemagick', fps=60)

def HeatmapGIF(t,SPICE_Obj, SkipFactor):


    # call the animator. blit=True means only re-draw the parts that
    # have changed.
    anim = animation.FuncAnimation(fig, animate_heatmap, init_func=init_heatmap,
                                   frames=math.ceil(len(t)/SkipFactor), interval=20, blit=True)
    anim.save('Heatmap_animation.gif', writer='imagemagick', fps=60)




def main():

    Title = """
       _____                         _   _       __      ___                 _ _
      / ____|                       | | (_)      \ \    / (_)               | (_)
     | (___  _   _ _ __   __ _ _ __ | |_ _  ___   \ \  / / _ ___ _   _  __ _| |_ _______ _ __
      \___ \| | | | '_ \ / _` | '_ \| __| |/ __|   \ \/ / | / __| | | |/ _` | | |_  / _ \ '__|
      ____) | |_| | | | | (_| | |_) | |_| | (__     \  /  | \__ \ |_| | (_| | | |/ /  __/ |
     |_____/ \__, |_| |_|\__,_| .__/ \__|_|\___|     \/   |_|___/\__,_|\__,_|_|_/___\___|_|
              __/ |           | |
             |___/            |_|

    Select a Data Set to Animate:
    (1) Transient Waveforms
    (2) Synapse Heatmap
    """

    mode = GetUserInput(Title)


    if mode == 1:
        TransientGIF(t,SPICE_Obj, SkipFactor)
    elif mode == 2:
        HeatmapGIF(t,SPICE_Obj, SkipFactor)
    else:
        print("Invalid Mode")


main()

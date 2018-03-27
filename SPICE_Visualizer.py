from LTSpiceRaw_Reader import LTSpiceRawRead

import numpy as np
import matplotlib.pyplot as plt

from matplotlib import animation, rc
import seaborn as sns; sns.set(color_codes = True)
import math


###############################33
# Some setup

# equivalent to rcParams['animation.html'] = 'html5'
rc('animation', html='html5')

# First set up the figure, the axis, and the plot element we want to animate
fig, ax = plt.subplots()

ax.set_xlim(( 0, 16.5))
ax.set_ylim((-1, 11))

plot1, = ax.plot([], [], lw=2)
plot2, = ax.plot([], [], lw=2)
plot3, = ax.plot([], [], lw=2)
plot4, = ax.plot([], [], lw=2)
plot5, = ax.plot([], [], lw=2)

########################################33
# Read in Part 1 data


SPICE_Obj = LTSpiceRawRead('Net Array_Small.raw')
print('SPICE Object Created')
SPICE_Obj.get_trace_names()

#Part 1, get the transient plots made

#Need time, audioin, neuronin, neuronin2, predict, predict2

t = SPICE_Obj.get_trace('time')
t = np.absolute(t.data)  # Weird thing going on w/ this and random negative numbers showing up.

audioin = SPICE_Obj.get_trace('V(audioin)').data
nIn1 = SPICE_Obj.get_trace('V(neuronin)').data
nIn2 = SPICE_Obj.get_trace('V(neuronin2)').data
pred1 = SPICE_Obj.get_trace('V(predict)').data
pred2 = SPICE_Obj.get_trace('V(predict2)').data
print('Transient Data Loaded')

"""
plt.plot(t,audioin, label='Audio')
plt.plot(t,nIn1, label='Post-Neuron 1 Input')
plt.plot(t,nIn2, label='Post-Neuron 2 Input')
plt.plot(t,pred1, label='Prediction 1')
plt.plot(t,pred2, label='Prediction 2')
plt.xlabel('Time (s)')
plt.ylabel('Voltage (V)')
plt.legend(loc='upper right')
plt.show()
"""


#############################################
# Read in Part 2 data

x_i = np.array(([1,2,6,10,15,21,17,24],[5,6,20,9,14,19,23,27,26]))
print('Heatmap Data Loaded')

SkipFactor = 5000

# initialization function: plot the background of each frame
def init():
    plot1.set_data([], [])
    plot2.set_data([], [])
    plot3.set_data([], [])
    plot4.set_data([], [])
    plot5.set_data([], [])
    return (plot1,plot2,plot3,plot4,plot5,)

# animation function. This is called sequentially
def animate(i):
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

# call the animator. blit=True means only re-draw the parts that
# have changed.
anim = animation.FuncAnimation(fig, animate, init_func=init,
                               frames=math.ceil(len(t)/SkipFactor), interval=20, blit=True)
anim.save('animation.gif', writer='imagemagick', fps=60)

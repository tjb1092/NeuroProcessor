from scipy.io import wavfile
import math

# For a given sound sample, find where the voice begins and when it ends.
def voiceTimings(filename):

    # Use Scipy wavefile reader to get the raw data.
    wavData = wavfile.read(filename)
    data = wavData[1]
    sampleRate = wavData[0]

    # Initialize flags and data
    risingEdge = False
    fallingEdge = False
    v_start = 0
    v_end = 0

    # Window Params:
    avgWindow = 50
    start_thresh = 100.0
    end_thresh = 50.0

    # Get a moving average of 50 samples.
    for i in range(int(avgWindow)-1,len(data)):
        # Use numpy slicing to calculate moving average
        movingAvg = sum(abs(data[(i-int(avgWindow)): i,0])) / avgWindow

        # At the first instance where the signal is greater than the thresh,
        # Say that the voice has started
        if movingAvg > start_thresh and not risingEdge:
            v_start = i / sampleRate
            risingEdge = True

        # At the first instance where the signal is less than the thresh,
        # Say that the voice has ended
        if (risingEdge and movingAvg < end_thresh and not fallingEdge
            and ((i/sampleRate) > v_start+0.3)):
            v_end = i/sampleRate
            fallingEdge = True

    if v_start == 0 or v_end == 0:
        # Some error checking until I'm fairly confident w/ process.
        print("Window not sensitive enough!")
        print(v_start)
        print(v_end)
        print("Sample Length:")
        print(len(data)/sampleRate)
        print("\n")

    else:
        print("Sample Start/End")
        print(v_start)
        print(v_end)
        print("Sample Length:")
        print(len(data)/sampleRate)
        print("\n")

    return [ v_start, v_end]

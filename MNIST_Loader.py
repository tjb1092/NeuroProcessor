import numpy as np
from mnist import MNIST
from SpiceModifier import SpiceWriter
mndata = MNIST('C:\\Users\\baile\\data\\mnist\\')
import cv2
import random
import math
import matplotlib.pyplot as plt

# Global Variables
width, height = 14, 14

vdd = 3.3  # Voltages will be relative to the process node voltage
vspk = 2.1
imax = 100e-6
imin = 1e-6

feature_length = 35
num_classes = 10

Toff = Ton = 0.015  # Duration of on vs. off time.
T_rf = 1e-7  # Rise and fall time


spkOn = 40e-6
minD = 70e-6
maxD = 490e-6
thresh = 0.1  # pixel intensity based on empirically looking.


def encode_digits(images, labels, initial_duration):

    # Scale images:
    im_scaled = np.zeros((len(images),feature_length))
    for istep, im in enumerate(images):
        im_scaled[istep] = np.multiply((-imax/1.0),im)

    # Now encode MNIST digits into 784 voltage sources w/ PWL functions
    # Input Struct: [pixel_num: [time, val]] - List of lists
    # Output Struct: [class_num: [time, val]]

    inputPattern = []
    outputPattern = []
    total_duration = initial_duration

    # Instantiate input list of numpy arrays:
    # a list of lists ate all of my memory. preallocation should be faster anywho.

    inputPattern = np.zeros((feature_length,len(im_scaled)*4+1,2))
    outputPattern = np.zeros((num_classes,len(im_scaled)*4+1,2))
    print(inputPattern.shape)

    # Implicitly define the end of one sample as the beginning of the next sample.
    for istep, im in enumerate(im_scaled):
        if istep % 1000 == 0:
            print(istep, total_duration)
        # Two loops: One for inputs and one for outputs.

        # Input loop: Go through each pixel in the image.
        # Transfer that array of pixels into one unit of the time-series input

        for pstep, pix in enumerate(im):
            # _
            temp_duration = total_duration

            temp_duration += Toff
            inputPattern[pstep][istep*4+1][:] = [temp_duration, 0.0]
            # _/
            temp_duration += T_rf
            inputPattern[pstep][istep*4+2][:] = [temp_duration, pix]
            # _/--
            temp_duration += Ton
            inputPattern[pstep][istep*4+3][:] = [temp_duration, pix]
            # _/--\
            temp_duration += T_rf
            inputPattern[pstep][istep*4+4][:] = [temp_duration, 0.0]


        total_duration = temp_duration  # Make last temp the total_duration
        # Output loop: loop over one input array. change to label where
        # appropriate for the correct label array. Leave rest as zeros.

        tmp = inputPattern[0] # Pull out first pixel's timing sequence.

        label = labels[istep]  # pull out the label for this sample.

        for c in range(num_classes):
            # Generate the timing for each output label class for this sample.
            if c == int(label):
                # Make the "correct" label output a label voltage.
                # Might need to flip this based on my logic definition.
                l_V = vdd
            else:
                l_V = 0.0

            # Use sample index to get the proper index from tmp.
            outputPattern[c][istep*4+1][:] = [tmp[istep*4+1][0], 0.0]
            outputPattern[c][istep*4+2][:] = [tmp[istep*4+2][0], l_V]
            outputPattern[c][istep*4+3][:] = [tmp[istep*4+3][0], l_V]
            outputPattern[c][istep*4+4][:] = [tmp[istep*4+4][0], 0.0]

    print("total_duration: {} s".format(total_duration))
    return(inputPattern, outputPattern, total_duration)


def encode_neuron(images, labels, initial_duration):


    # Now encode MNIST digits into 196 voltage sources w/ PWL functions
    # Input Struct: [pixel_num: [time, val]] - List of lists
    # Output Struct: [class_num: [time, val]]

    inputPattern = []
    outputPattern = []
    total_duration = initial_duration

    # Instantiate input list of numpy arrays:
    # a list of lists ate all of my memory. preallocation should be faster anywho.

    inputPattern = [np.zeros((1,2)) for x in range(196)]
    # Not guaranteed that the timings will line up exactly
    durations = np.zeros((feature_length))
    for i in range(len(durations)):
        durations[i] = initial_duration

    outputPattern = np.zeros((num_classes,len(images)*4+1,2))
    lstart = 0
    # Implicitly define the end of one sample as the beginning of the next sample.
    for istep, im in enumerate(images):
        if istep % 1000 == 0:
            print(istep, durations[0])
        # Two loops: One for inputs and one for outputs.

        # Input loop: Go through each pixel in the image.
        # Transfer that array of pixels into one unit of the time-series input

        for pstep, pix in enumerate(im):
            # _
            temp_duration = durations[pstep]
            spklimit = temp_duration + Ton
            d = 544e-6 *(pix-1) + 490e-6  # Linear eq. ranging from 70um to 490um delays

            while (temp_duration + d + spkOn) < spklimit:
                # ensure that the spikes will never be longer than Ton
                if pix < thresh:
                    # Neuron is off this sample.
                    temp_duration = spklimit
                    inputPattern[pstep] = np.append(inputPattern[pstep], [temp_duration, 0.0])
                    break
                else:

                    # make neuron spike during application of sample prop to pix val.
                    #_
                    # Compute delay
                    temp_duration += d
                    inputPattern[pstep] = np.append(inputPattern[pstep], [temp_duration, 0.0])
                    # _/
                    temp_duration += T_rf
                    inputPattern[pstep] = np.append(inputPattern[pstep], [temp_duration, vspk])
                    # _/--
                    temp_duration += spkOn
                    inputPattern[pstep] = np.append(inputPattern[pstep], [temp_duration, vspk])
                    # _/--\
                    temp_duration += T_rf
                    inputPattern[pstep] = np.append(inputPattern[pstep], [temp_duration, 0.0])

            temp_duration = spklimit
            inputPattern[pstep] = np.append(inputPattern[pstep], [temp_duration, 0.0])  # even out the end of the sample
            durations[pstep] = temp_duration  # Make last temp the total_duration

        # Output loop: loop over one input array. change to label where
        # appropriate for the correct label array. Leave rest as zeros.

        lend = spklimit
        label = labels[istep]  # pull out the label for this sample.

        for c in range(num_classes):
            # Generate the timing for each output label class for this sample.
            if c == int(label):
                # Make the "correct" label output a label voltage.
                # Might need to flip this based on my logic definition.
                l_V = vdd
            else:
                l_V = 0.0

            # Use sample index to get the proper index from tmp.
            outputPattern[c][istep*4+1][:] = [lstart, 0.0]
            outputPattern[c][istep*4+2][:] = [lstart + T_rf, l_V]
            outputPattern[c][istep*4+3][:] = [lend - T_rf, l_V]
            outputPattern[c][istep*4+4][:] = [lend, 0.0]
        lstart = lend

    print("total_duration: {} s".format(durations[0]))
    return(inputPattern, outputPattern, durations[0])

def Generate_IO_Neuron(content, pattern, name, T_T):
    if name == "l":
        p_shape = pattern.shape
        num_sources = p_shape[0]  # Index the first term in shape.
    else:
        num_sources = len(pattern)

    source_counter = 0

    if name == "i":
        prefix = "i"
    else:
        prefix = "v"

    for source in range(num_sources):
        # Note, voltage sources need to be serially connected, current src is parallel
        if T_T == 1:
            # Training Source
            t_t = "tr"
            if name == "l":
                vi = "vl{}".format(source)
                vo = 0
            else:
                vi = "niout{}".format(source)
                vo = "vtr{}".format(source)

        else:
            # Testing Source
            print(source)
            t_t = "te"
            vi = "vtr{}".format(source)
            vo = 0

        #For each source, append the correct information per sample to the string.
        newString = "{}{}{}{} {} {} pwl(".format(prefix, name, source, t_t,  vi, vo)
        if source == 35:
            print(pattern[source])
        for row in pattern[source]:
            if name == "l":
                newString += " {0:.7f} {1:.7f}".format(row[0], row[1])
            else:
                newString += " {0:.7f}".format(row)

        newString += ")\n"
        content.append(newString)



def test_loader():
    # Some simple test data to try out
    samples = np.array(((0, 0, 1, 0, 0, 1, 0, 0, 1),
                        (1, 1, 1, 0, 0, 0, 0, 0, 0),
                        (0, 0, 0, 1, 1, 1, 0, 0, 0),
                        (0, 0, 0, 0, 0, 0, 1, 1, 1),
                        (1, 0, 0, 1, 0, 0, 1, 0, 0),
                        (0, 1, 0, 0, 1, 0, 0, 1, 0)))
    labels = np.array(((0),
                        (1),
                        (2),
                        (3),
                        (4),
                        (5)))
    print(samples.shape, labels.shape)
    return samples, labels

def smallDigit_loader():
    # Some simple test data to try out
    samples = np.array(((1, 1, 1, 1, 1,
                         1, 0, 0, 0, 1,
                         1, 0, 0, 0, 1,
                         1, 0, 0, 0, 1,
                         1, 0, 0, 0, 1,
                         1, 0, 0, 0, 1,
                         1, 1, 1, 1, 1),
                        (0, 1, 1, 1, 0,
                         1, 0, 0, 0, 1,
                         1, 0, 0, 0, 1,
                         1, 0, 0, 0, 1,
                         1, 0, 0, 0, 1,
                         1, 0, 0, 0, 1,
                         0, 1, 1, 1, 0),
                        (0, 1, 1, 1, 0,
                         1, 0, 0, 0, 1,
                         1, 0, 0, 0, 1,
                         1, 0, 1, 1, 1,
                         1, 1, 1, 0, 1,
                         1, 0, 0, 0, 1,
                         0, 1, 1, 1, 0),
                        (0, 0, 1, 0, 0,
                         0, 0, 1, 0, 0,
                         0, 0, 1, 0, 0,
                         0, 0, 1, 0, 0,
                         0, 0, 1, 0, 0,
                         0, 0, 1, 0, 0,
                         0, 0, 1, 0, 0),
                        (0, 0, 1, 0, 0,
                         0, 1, 1, 0, 0,
                         1, 0, 1, 0, 0,
                         0, 0, 1, 0, 0,
                         0, 0, 1, 0, 0,
                         0, 0, 1, 0, 0,
                         0, 0, 1, 0, 0),
                        (0, 0, 1, 0, 0,
                         0, 1, 1, 0, 0,
                         1, 0, 1, 0, 0,
                         0, 0, 1, 0, 0,
                         0, 0, 1, 0, 0,
                         0, 0, 1, 0, 0,
                         1, 1, 1, 1, 1),
                        (1, 1, 1, 1, 1,
                         0, 0, 0, 0, 1,
                         0, 0, 0, 0, 1,
                         1, 1, 1, 1, 1,
                         1, 0, 0, 0, 0,
                         1, 0, 0, 0, 0,
                         1, 1, 1, 1, 1),
                        (0, 1, 1, 1, 0,
                         1, 0, 0, 0, 1,
                         0, 0, 0, 0, 1,
                         0, 0, 0, 1, 1,
                         0, 1, 1, 0, 0,
                         1, 0, 0, 0, 0,
                         1, 1, 1, 1, 1),
                        (1, 1, 1, 1, 1,
                         0, 0, 0, 0, 1,
                         0, 0, 0, 0, 1,
                         0, 0, 1, 1, 0,
                         0, 1, 1, 0, 0,
                         1, 0, 0, 0, 0,
                         1, 1, 1, 1, 1)))
    labels = np.array(((0),
                        (0),
                        (0),
                        (1),
                        (1),
                        (1),
                        (2),
                        (2),
                        (2),
                        (3),
                        (3),
                        (3),
                        (4),
                        (4),
                        (4),
                        (5),
                        (5),
                        (5),
                        (6),
                        (6),
                        (6),
                        (7),
                        (7),
                        (7),
                        (8),
                        (8),
                        (8),
                        (9),
                        (9),
                        (9)))

    print(samples.shape, labels.shape)
    return samples, labels

def smallerDigit_loader():
    # Some simple test data to try out
    samples = np.array(((0, 1, 1, 1, 0,
                         1, 0, 0, 0, 1,
                         1, 0, 0, 0, 1,
                         1, 0, 0, 0, 1,
                         1, 0, 0, 0, 1,
                         1, 0, 0, 0, 1,
                         0, 1, 1, 1, 0),
                        (0, 0, 1, 0, 0,
                         0, 1, 1, 0, 0,
                         1, 0, 1, 0, 0,
                         0, 0, 1, 0, 0,
                         0, 0, 1, 0, 0,
                         0, 0, 1, 0, 0,
                         0, 0, 1, 0, 0),
                        (1, 1, 1, 1, 1,
                         0, 0, 0, 0, 1,
                         0, 0, 0, 0, 1,
                         0, 0, 1, 1, 0,
                         0, 1, 1, 0, 0,
                         1, 0, 0, 0, 0,
                         1, 1, 1, 1, 1)))
    labels = np.array(((0),
                        (1),
                        (2)))

    print(samples.shape, labels.shape)
    return samples, labels

def Generate_IO_Voltages(content, pattern, name, T_T):
    p_shape = pattern.shape
    num_sources = p_shape[0]  # Index the first term in shape.

    source_counter = 0

    if name == "i":
        prefix = "i"
    else:
        prefix = "v"

    for source in range(num_sources):
        # Note, voltage sources need to be serially connected, current src is parallel
        if T_T == 1:
            # Training Source
            t_t = "tr"
        else:
            # Testing Source
            t_t = "te"
        vi = "v{}{}".format(name, source)
        vo = 0

        #For each source, append the correct information per sample to the string.
        newString = "{}{}{}{} {} {} pwl(".format(prefix, name, source, t_t,  vi, vo)

        for row in pattern[source]:
            newString += " {0:.7f} {1}".format(row[0], row[1])

        newString += ")\n"
        content.append(newString)

def data_load(fn):
    # Open text file and create and read in each line
    X_array = []
    with open(fn) as f:
    	contents = f.readlines()
    # for each line
    for data in contents:
        parsedData = data.split("\t")  # Split via space deliminator
        parsedData[-1] = parsedData[-1][:-1]  #remove new-line character
        # Create data tuple by casting text to floats and add label

        row = np.zeros((784))
        for i, feature in enumerate(parsedData):
            row[i] = float(feature)
        row = row.reshape(28,28)
        row = cv2.resize(row,(width,height))

        row = row.reshape(width*height)
        X_array.append(row)

    return X_array

def label_load(fn):
	label_array = []
	with open(fn) as f:
		contents = f.readlines()
	# for each line
	for label in contents:
		label = label[:-1]  #remove new-line character
		label_array.append(label)  # Convert to int

	return label_array


def create_train_test_split(x, y, percent):
	# Create Train/Test Split
	d_len = len(x)
	# Sample 80% of the indices
	train_index = random.sample(range(d_len - 1), math.ceil(percent*d_len))
	# Compute the remaining 20% of samples for the test set
	test_index = list(set(range(d_len-1)) - set(train_index))

	# Index out the train set from the total set
	x_train = x[train_index]
	y_train = y[train_index]
	# Index the test set
	x_test = x[test_index]
	y_test = y[test_index]

	# create data dict to pass up to other functions
	return {"x_train": x_train, "y_train": y_train, "x_test": x_test, "y_test": y_test}

def preprocessData():
	# Read in data
	Xfn = "MNISTnumImages5000.txt"
	yfn = "MNISTnumLabels5000.txt"

	# Pass data array into functions to append everything together
	X = data_load(Xfn)
	y = label_load(yfn)
	ones = np.ones((len(X), 1))

	X = np.asarray(X)  # Convert to numpy array
	y = np.asarray(y)  # Convert to numpy array
	# Data already normalized.
	return X, y

def pick_digits(X,y):
    counters = np.zeros(10)
    s_thresh = 10
    X_new = []
    y_new = []
    for i, im in enumerate(X):
        label = int(y[i])
        if counters[label] < s_thresh:
            X_new.append(im)
            y_new.append(y[i])
            counters[label] += 1
    return X_new, y_new


def flipbits(im, num):
    # for the image, flip num number of bits randomly
    #sample without replacement
    bits = np.random.choice(len(im), num, replace=False)
    for bit in bits:
        im[bit] = int(not im[bit])  #flip the bit
    return im

def main():
    isMNIST = False
    encode_neurons = False
    flip_bits = True
    change_order = False
    num_bits = 5
    if isMNIST:
        # Loads MNIST into python arrays. Not numpy here.
        X, y = preprocessData()

        data = create_train_test_split(X, y, 0.8)
        im_train = data["x_train"]
        im_test = data["x_test"]
        label_train = data["y_train"]

        im_train, label_train = pick_digits(im_train, label_train)
        label_test = label_train
        im_test = im_train
    else:

        im_train, label_train = smallerDigit_loader()
        im_test, label_test = smallerDigit_loader()

    if flip_bits:
        for i, im in enumerate(im_test):
            im_test[i] = flipbits(im, num_bits)

        for i in range(3):
            print(im_train[i])
            print(im_test[i])
            print("\n")


    if change_order:
        order = np.array(range(len(im_train)))
        random.shuffle(order)
        im_train = im_train[order]
        label_train = label_train[order]
        print(label_train, label_test)

    print(label_train)
    input("pasue")
    if encode_neurons:
        print("Generating voltages for training:")
        input_train, output_train, train_duration = encode_neuron(im_train, label_train, 0)

        print("Generating voltages for testing:")
        input_test, output_test, total_duration = encode_neuron(im_test, label_test, train_duration)
        content = []
        Generate_IO_Neuron(content, input_train, "v", 1)
        Generate_IO_Neuron(content, output_train, "l", 1)
        Generate_IO_Neuron(content, input_test, "v", 0)
    else:
        print("Generating voltages for training:")
        input_train, output_train, train_duration = encode_digits(im_train, label_train, 0)

        print("Generating voltages for testing:")
        input_test, output_test, total_duration = encode_digits(im_test, label_test, train_duration)

        content = []
        Generate_IO_Voltages(content, input_train, "i", 1)
        Generate_IO_Voltages(content, output_train, "l", 1)
        Generate_IO_Voltages(content, input_test, "i", 0)
    # Add training Signal
    newString = "vTrain train 0 pwl(0.0 vdd {} vdd {} 0V)".format(train_duration, train_duration+(0.1*Toff))
    content.append(newString)

    voltage_element_fn = "DigitFiles/VoltageSources{}.sp".format(num_bits)
    SpiceWriter(content, voltage_element_fn)

if __name__ == "__main__":
    main()

import numpy as np
from mnist import MNIST
from SpiceModifier import SpiceWriter
mndata = MNIST('/home/tonyjb/MNIST')

# Some global vars
vdd = 3.3  # Voltages will be relative to the process node voltage
#feature_length = 784
#num_classes = 10
feature_length = 9
num_classes = 8

Toff = Ton = 0.0005  # Duration of on vs. off time.
T_rf = 1e-7  # Rise and fall time
# To get the training set sent through the network in the time frame the STPRAM
# will understand, I'll probably need to reduce this to .1ms - > training of 6sec.



def encode_digits(images, labels, initial_duration):

    # Scale images:
    im_scaled = np.zeros((len(images),feature_length))
    for istep, im in enumerate(images):
        im_scaled[istep] = np.multiply((vdd/255.0),im)

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

            if c == label:
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

def test_loader():
    # Some simple test data to try out
    samples = np.array(((0, 255, 0, 255, 0, 255, 0, 255, 0),
                        (255, 0, 255, 0, 255, 0, 255, 0, 255),
                        (0,  0, 255, 0, 0, 255, 0, 0, 255),
                        (255, 255, 255, 0, 0, 0, 0, 0, 0),
                        (0, 0, 0, 255, 255, 255, 0, 0, 0),
                        (0, 0, 0, 0, 0, 0, 255, 255, 255),
                        (255, 0, 0, 255, 0, 0, 255, 0, 0),
                        (0, 255, 0, 0, 255, 0, 0, 255, 0)))
    labels = np.array(((0),
                        (1),
                        (2),
                        (3),
                        (4),
                        (5),
                        (6),
                        (7)))
    print(samples.shape, labels.shape)
    return samples, labels


def Generate_IO_Voltages(content, pattern, name, T_T):
    p_shape = pattern.shape
    num_sources = p_shape[0]  # Index the first term in shapeself.

    for source in range(num_sources):

        if T_T == 1:
            # Training Source
            vi = "v{}{}".format(name, source)
            vo = "v{}{}t".format(name, source)
            t_t = "tr"
        else:
            # Testing Source
            vi = "v{}{}t".format(name, source)
            vo = "0"
            t_t = "te"


        #For each source, append the correct information per sample to the string.
        newString = "V{}{}{} {} {} pwl(".format(name, source, t_t,  vi, vo)

        for row in pattern[source]:
            newString += " {0:.7f} {1:.3f}".format(row[0], row[1])

        newString += ")\n"
        content.append(newString) #Override template w/ new command

    # Write out newly modified file into the main directory



def test_loader():
    # Some simple test data to try out
    samples = np.array(((0, 255, 0, 255, 0, 255, 0, 255, 0),
                        (255, 0, 255, 0, 255, 0, 255, 0, 255),
                        (0,  0, 255, 0, 0, 255, 0, 0, 255),
                        (255, 255, 255, 0, 0, 0, 0, 0, 0),
                        (0, 0, 0, 255, 255, 255, 0, 0, 0),
                        (0, 0, 0, 0, 0, 0, 255, 255, 255),
                        (255, 0, 0, 255, 0, 0, 255, 0, 0),
                        (0, 255, 0, 0, 255, 0, 0, 255, 0)))
    labels = np.array(((0),
                        (1),
                        (2),
                        (3),
                        (4),
                        (5),
                        (6),
                        (7)))
    print(samples.shape, labels.shape)
    return samples, labels


def main():


    isMNIST = False

    if isMNIST:
        # Loads MNIST into python arrays. Not numpy here.
        im_train, label_train = mndata.load_training()
        im_test, label_test = mndata.load_testing()
    else:
        im_train, label_train = test_loader()
        im_test, label_test = test_loader()


    print("Generating voltages for training:")
    input_train, output_train, train_duration = encode_digits(im_train, label_train, 0)

    # Add a "isTraining" signal based on train_duration!

    print("Generating voltages for testing:")
    input_test, output_test, total_duration = encode_digits(im_test, label_test, train_duration)

    content = []
    Generate_IO_Voltages(content, input_train, "i", 1)
    Generate_IO_Voltages(content, output_train, "l", 1)
    Generate_IO_Voltages(content, input_test, "i", 0)
    Generate_IO_Voltages(content, output_test, "l", 0)


    voltage_element_fn = "DigitFiles/VoltageSources.sp"
    SpiceWriter(content, voltage_element_fn)

if __name__ == "__main__":
    main()

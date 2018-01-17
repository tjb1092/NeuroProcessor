from pydub import AudioSegment
import os
import tkinter
#dir = os.path.dirname(__file__)
from tkinter.filedialog import askopenfilename
filename = askopenfilename()
tkinter.Tk().withdraw()
#AudioFolder = os.path.join(dir, '/relative/path/to/file/you/want')

sound1 = AudioSegment.from_wav("amy.wav")
sound2 = AudioSegment.from_wav("eric.wav")

combined_sounds = sound1 + sound2 * 2

combined_sounds.export("monstrosity.wav")

#def TestStruct():
#    def __init__:
#        self.plan = [];
#        print("struct made!")

#    def Add

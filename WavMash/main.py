from pydub import AudioSegment

sound1 = AudioSegment.from_wav("amy.wav")
sound2 = AudioSegment.from_wav("eric.wav")

combined_sounds = sound1 + sound2 * 2

combined_sounds.export("monstrosity.wav")


#def TestStruct():
#    def __init__:
#        self.plan = [];
#        print("struct made!")

#    def Add

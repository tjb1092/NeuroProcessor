import sys
import os
from PyQt4 import QtGui, QtCore
#from pydub import AudioSegment

class Window(QtGui.QMainWindow):

    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(50,50,500,300)
        self.setWindowTitle("PyQT Tutorial")
        self.setWindowIcon(QtGui.QIcon('logo.ico'))

        # Define the menu options
        extractAction = QtGui.QAction("&Get to the choppah", self)
        extractAction.setShortcut("Ctrl+Q")
        extractAction.setStatusTip('Leave The App')
        extractAction.triggered.connect(self.close_application)

        self.statusBar()

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File') # Add extractAction to file
        fileMenu.addAction(extractAction)

        self.home()


    def home(self):
        btn = QtGui.QPushButton("Quit", self)
        btn.clicked.connect(self.close_application)
        btn.resize(btn.sizeHint())
        btn.move(0,100)

        #extractAction = QtGui.QAction(QtGui.QIcon('loco.ico'))

        self.show()


    def close_application(self):
        print("dis is custom")
        sys.exit()

def main():

    app = QtGui.QApplication(sys.argv)
    GUI = Window()
    sys.exit(app.exec_())

main()


#AudioFolder = os.path.join(dir, '/relative/path/to/file/you/want')


#sound1 = AudioSegment.from_wav("amy.wav")
#sound2 = AudioSegment.from_wav("eric.wav")

#combined_sounds = sound1 + sound2 * 2

#combined_sounds.export("monstrosity.wav")

# def TestStruct():
#    def __init__:
#        self.plan = [];
#        print("struct made!")

#    def Add

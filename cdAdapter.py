import subprocess
import os

from PyQt5.QtCore import QProcess


class CDAdapter:
    burnProcess = None
    # getting names of all wifi
    def write(self, names):
        info = "/dev/sr0"
        self.burnProcess = QProcess()
        #umount /dev/sr0 & xorriso -outdev /dev/sr0 -blank as_needed map /home/alexey/Music/Bass-Drum-2.wav /sound/Bass-Drum-2.wav commit_eject all 2>&1
        ex = " umount " + info + " & xorriso -outdev " + info + " -blank as_needed"
        print(names)
        for rec in names:
            ex =  ex + " map " + rec["path"] + " /files/" + rec["name"]
        ex = ex + " commit_eject all 2>&1"
        list = []
        list.append("-c")
        list.append(ex)
        self.burnProcess.start("sh", list)
        return "writing..."


    def notify(self):
        readline = self.burnProcess.readAllStandardOutput()
        print(readline)



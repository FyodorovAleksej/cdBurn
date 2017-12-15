import subprocess
import os

class CDAdapter:
    # getting names of all wifi
    def write(self, names):
        # connecting to ssid
        text = ""
        for i in names:
            text = text + i["path"] + " /"+ i["name"] + " "
        subprocess.call("umount /dev/sr0 & xorriso -outdev /dev/sr0 -blank as_needed map " + text + "commit_eject all", shell=True)
        return "writing..."
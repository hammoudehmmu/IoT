from subprocess import call
from sys import argv
from os import chdir, getcwd

callForm = ["make", "micaz", "", "mib510,/dev/ttyUSB0"]
baseDir = getcwd()
doWait = False
for arg in argv[1:]:
    if doWait:
        raw_input("Press Enter to continue")
    arg = arg.split(".")
    fileLoc, nodeId = arg[0], arg[1]
    chdir(fileLoc)
    callForm[2] = "install."+nodeId
    retcode = call(callForm)
    doWait = True

from subprocess import call
from sys import argv

callForm = ["make", "micaz", "", "mib510,/dev/ttyUSB0"]
doWait = False
tasks = []
for arg in argv[1:]:
    arg = str(arg).split("/")
    if "-" in arg[1]:
        ids = arg[1].split("-")
        for n in range(int(ids[0]), int(ids[1])+1):
            tasks.append((arg[0], str(n)))
    else:
        tasks.append((arg[0], arg[1]))
for arg in tasks:
    if doWait:
        raw_input("Press Enter to continue")
    fileLoc, nodeId = arg[0], arg[1]
    callForm[2] = "install."+nodeId
    retcode = call(callForm, cwd=fileLoc)
    if retcode != 0:
        break
    doWait = True

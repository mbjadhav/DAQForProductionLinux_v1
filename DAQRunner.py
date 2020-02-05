from BetaDAQ import *
from general import *
import subprocess

editor = GetEditor("gedit")

if __name__ == "__main__":
    print(" \n BetaScope DAQ is created \n")

    mode = ["beta", "ts"]

    print("\n *** Open Configuration file *** \n")
    editConfig = raw_input("\nDo you want to edit BetaDAQ_Config?[y/n]: ")
    if "y" in editConfig:
        subprocess.call([editor, "BetaDAQ_Config.ini"])
        raw_input("\nProceed ahead?[y]: ")
    DAQ = BetaDAQ("BetaDAQ_Config.ini")
    
    runningMode = raw_input("\nIs it a Beta Measurement?[y/n]: ")
    if "y" in runningMode:
        DAQ.BetaMeas()
#    elif "ts" in runningMode:
#        DAQ.ThreshodVsPeriod()
    else:
        print("Invalid running Mode (please enter 'Y' for Beta Measurements)")

    print("DAQ is closed")

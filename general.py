'''
functions for testing and general purpose
'''
import sys, os
import time

def progress(mode=1):
    def progress_1(content, numParsed, total):
        percentage = (1.0*numParsed/total)*100.0
        sys.stdout.flush()
        sys.stdout.write("\r"+str(content)+ " " + str(percentage) + "%")
        #time.sleep(0.005)
    def progress_2(content, content2):
        sys.stdout.write("\r"+str(content)+ " " + str(content2) +"\r")
        sys.stdout.flush()
        #time.sleep(0.1)

    if mode == 1:
        return progress_1
    else:
        return progress_2

#progress=progress(2)
#for i in range(1000):
    #progress("test {}".format(i*i), " fu {}".format("hi"))
    #progress("test {}".format(i*i), i, 1000)

#raw_input()

def GetEditor( whichEditor ):
    EDITOR = os.environ.get("EDITOR", str(whichEditor) )
    return EDITOR


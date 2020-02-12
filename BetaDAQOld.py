from DAQConfigReader import *
from DAQProducer import *
from Data_Path_Setup import *
from ROOTClass import *
from general import *
import gc
import datetime
import time
import subprocess
import shutil
import numpy as np

class BetaDAQ:
    def __init__(self, configFileName):
        print("Using Beta DAQ class...XDDDDDDDDDDDDDDDD")
        self.configFile = DAQConfig()
        self.configFile.ReadDAQConfig( configFileName )

    def BetaMeas(self):
        print("Using Beta Measurement scripts")

        MASTER_PATH = self.configFile.DAQMasterDir
        PARENT_DIR = self.configFile.DAQDataDir
        Setup_Data_Folder( self.configFile.DAQMasterDir, self.configFile.DAQDataDir, self.configFile.RunNumber )
        CURRENT_FILE = Setup_Imon_File( self.configFile.RunNumber )
        CURRENT_FILE = Check_Imon_File( CURRENT_FILE )

        current_file = open(CURRENT_FILE, "w")

        descriptionFile = raw_input("\n Create description file?[y/n]: ")
        if "y" in descriptionFile:
            editor = GetEditor("gedit")
            CreateDescription( self.configFile.RunNumber )
            subprocess.call([editor, "Sr_Run_" + str(self.configFile.RunNumber) + "_Description.ini"])
        else:
            pass
        shutil.copy("Sr_Run_" + str(self.configFile.RunNumber) + "_Description.ini",  "/home/labuser/betaspectra/DAQlog/")

        Scope = ScopeProducer( self.configFile )
        PowerSupply = PowerSupplyProducer( self.configFile )
        PowerSupply.SetVoltage(self.configFile.PSTriggerChannel, self.configFile.TriggerVoltage)

        for i in range(len(self.configFile.FileNameList)):
            PowerSupply.SetVoltage( self.configFile.PSDUTChannel, self.configFile.VoltageList[i] )
            V_Check = PowerSupply.ConfirmVoltage( self.configFile.PSDUTChannel, self.configFile.VoltageList[i] )
            if V_Check:
                dataFileName = self.configFile.FileNameList[i]+".root"
                outROOTFile = ROOTFileOutput(dataFileName, self.configFile.EnableChannelList )
                print("Ready for data taking")

                current_100cycle = 0.0
                start_time = time.time()
                event = 0
                fail_counter = 0
                while event < self.configFile.NumEvent:
                    event += 1
                    Scope.WaitForTrigger()
                    #print("pass wait")
                    outROOTFile.i_timestamp[0] = time.time()
                    if event==0 or event%50==0:
                        current_100cycle = PowerSupply.CurrentReader( self.configFile.PSDUTChannel )
                    outROOTFile.i_current[0] = current_100cycle
                    waveData = ""
                    try:
                        waveData = Scope.GetWaveform( self.configFile.EnableChannelList, "ascii")
                    #print("took waveform")
                    except:
                        event -= 1
                        fail_counter += 1
                        print("fail getting data. {}".format(fail_counter))
                        if fail_counter == 100000:
                            break
                        else:
                            continue

                    if len(waveData) == 0:
                        event -= 1
                        print("empty waveData...Please report this issue")
                        continue
                    elif len(waveData[0]) != len(self.configFile.EnableChannelList ):
                        event -= 1
                        print("waveData and channel mismatch, Please report this issue")
                        continue
                    else:
                        pass

                    for ch in range(len(self.configFile.EnableChannelList)):
                        for j in range( len(waveData[0][ch]) ):
                            try:
                                outROOTFile.w[ch].push_back( float(waveData[1][ch][j]) )
                                outROOTFile.t[ch].push_back( waveData[0][ch][j] )
                            except:
                                if j == 0:
                                    print("push_back( float(waveData[1][ch][j]) ) error")
                                      #outROOTFile.w[ch].push_back(0)
                                      #outROOTFile.t[ch].push_back(0)
                                continue
                    outROOTFile.Fill()
                    waveData = []
                    waveData = ""
                    gc.collect()
                    if(event%1==0):
                        date = datetime.datetime.now()
                        print("[{}] Saved event on local disk : {}".format(str(date), event))
                outROOTFile.Close()
                currentAfter = PowerSupply.CurrentReader( self.configFile.PSDUTChannel )
                current_file.write("{}:{}:{}\n".format(self.configFile.VoltageList[i], "After", currentAfter))
                end_time = time.time()
                print("Rate = {}/s".format(self.configFile.NumEvent/(end_time-start_time)))
            else:
                print("Voltage dose not matche!")

        current_file.close()
        PowerSupply.Close()
'''
    def ThreshodVsPeriod(self):
        print("Using Threshold vs Period Scan scripts")
        progress = general.progress(1)
        Scope = ScopeProducer( self.configFile )
        PowerSupply = PowerSupplyProducer( self.configFile )
        MASTER_PATH = self.configFile.DAQMasterDir
        PARENT_DIR = self.configFile.DAQDataDir
        Setup_Data_Folder( self.configFile.DAQMasterDir, self.configFile.DAQDataDir, self.configFile.RunNumber )

        for i in range(len(self.configFile.ThresholdScan_VoltageList)):
            PowerSupply.SetVoltage( self.configFile.ThresholdScan_PSChannel, self.configFile.ThresholdScan_VoltageList[i] )
            V_Check = PowerSupply.ConfirmVoltage( self.configFile.ThresholdScan_PSChannel, self.configFile.ThresholdScan_VoltageList[i] )
            if V_Check:
                outFileName = self.configFile.ThresholdScan_FileNameList[i] + ".text"
                outFile = open(outFileName, "w")
                outFile.write("Threshold[V],Period[s],STD,NumEvent\n")
                print("Ready...")

                ini_threshold = self.configFile.ThresholdScan_StartValue
                while ini_threshold <= self.configFile.ThresholdScan_EndValue:
                    if ini_threshold < 0:
                        Scope.SetTrigger( self.configFile.ThresholdScan_ScopeChannel, ini_threshold, "NEG", "STOP")
                        Scope.Scope.inst.write("BUZZ ON;")
                        sleep(2)
                    else:
                        Scope.SetTrigger( self.configFile.ThresholdScan_ScopeChannel, ini_threshold, "POS", "STOP")
                        Scope.Scope.inst.write("BUZZ ON;")
                        sleep(2)
                    count = 1
                    t_0 = time.time()
                    startT = t_0
                    triggerCounter = []
                    endT = ""
                    timeout = self.configFile.ThresholdScan_Timeout
                    while count <= self.configFile.ThresholdScan_MaxEvent:
                        next = Scope.WaitForTrigger( timeout, "Th Scan")
                        deltaT = time.time()-t_0
                        if deltaT >= timeout-0.1:
                            endT = time.time()
                            break
                        if time.time()-startT > self.configFile.ThresholdScan_MaxTime:
                            print("\nExceed data taking max time {}".format(startT))
                            endT = time.time()
                            break
                        if "1" in next:
                            t_0 = time.time()
                            waveform_data = Scope.GetWaveform(int(self.configFile.ThresholdScan_ScopeChannel), "binary raw")
                            trigger_Tdiff = trcReader(waveform_data[0], "Trigger_Tdiff", self.configFile.ThresholdScan_ScopeChannel, "sequence_mode")
                            for k in range(len(trigger_Tdiff)-1):
                                triggerCounter.append( trigger_Tdiff[i+1][0]-trigger_Tdiff[i][0] )
                            count+=1
                        else:
                            pass
                        if count%100==0:
                            tmp = np.array(triggerCounter)
                            avg = np.mean(tmp)
                            progress("Period Mean: {}   Finisehd".format(avg), count, self.configFile.ThresholdScan_MaxEvent )
                    triggerCounter = np.array(triggerCounter)
                    period = ""
                    if count > self.configFile.ThresholdScan_MaxEvent:
                        period = np.mean(triggerCounter)
                        std = np.std(triggerCounter)
                    else:
                        period = np.mean(triggerCounter)
                        std = np.std(triggerCounter)
                    outFile.write("{},{},{},{}\n".format(ini_threshold,period,std,len(triggerCounter)))
                    print("Results: {},{},{},{}\n".format(ini_threshold,period,std,len(triggerCounter)))
                    outFile.flush()
                    ini_threshold += self.configFile.ThresholdScan_Step
                    print("Next threshold : {}".format(ini_threshold))
                outFile.close()
                print("Moving to next voltage...")
        PowerSupply.Close()
        print("Finished!")
'''

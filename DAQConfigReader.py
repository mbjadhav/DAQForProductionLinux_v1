'''
DAQ Configuration reader class
'''
import sys
import configparser
#if sys.version_info[0] == 2:
#    import ConfigParser as configparser
#else:
#    import configparser
#import os

class DAQConfig:
    def __init__(self):
        '''
        initializing DAQ configuration parameters
        '''

        self.ScopeName = ""

        self.VoltageList = []
        self.NumEvent = -1
        self.TriggerVoltage = ""
        self.RunNumber = ""
        self.DAQDataDir = ""

        self.FileNameList = []
        self.FileNameSuffix = ""

        self.ScopeIP = ""
        self.EnableChannelList = []
        self.TriggerChannel = ""
        self.DUTChannelList = ""
        self.TriggerSetting = []

        self.PSChannelList = []
        self.PSDUTChannel = ""
        self.PSTriggerChannel = ""
        self.PSSoftwareCompliance = ""

        self.DAQMasterDir = ""

        self.ThresholdScan_VoltageList = []
        self.ThresholdScan_FileList = []
        self.ThresholdScan_ScopeChannel = ""
        self.ThresholdScan_PSChannel = ""
        self.ThresholdScan_StartValue = ""
        self.ThresholdScan_EndValue = ""
        self.ThresholdScan_Step = "" #in volt
        self.ThresholdScan_Timeout = "" #in second
        self.ThresholdScan_MaxTime = ""
        self.ThresholdScan_MaxEvent = ""

    def ReadDAQConfig(self, configFileName):
        configFile = configparser.ConfigParser()
        try:
            configFile.read( configFileName )
            print("DAQ configuration file is read")
        except:
            print("Cannot find DAQ configuration file. Exiting")
            os.exit()

        self.ScopeName = str(configFile["Oscilloscope"]["SCOPE_NAME"])

        self.VoltageList = [ int(x) for x in configFile["Voltage_Scan"]["VOLTAGE_LIST"].split(",") ]
        self.NumEvent = int(configFile["Voltage_Scan"]["nEvent"])
        self.TriggerVoltage = int(configFile["Trigger_Setting"]["TRIGGER_VOLTAGE"])
        self.RunNumber = str(configFile["File_Name"]["RUN_NUMBER"])
        self.FileNameSuffix = "trig"+str(self.TriggerVoltage) +"V"

        for volt in self.VoltageList:
            self.FileNameList.append( str("Sr_Run"+str(self.RunNumber)+"_"+str(volt)+"V_"+self.FileNameSuffix ) )
        print("File name list is created:")
        print(self.FileNameList)

        self.ScopeIP = str(configFile["Oscilloscope"]["SCOPE_IP_ADDRESS"])
        self.EnableChannelList = [ int(x) for x in configFile["Oscilloscope"]["ENABLE_CHANNEL"].split(",") ]
        self.DUTChannelList = [ int(x) for x in configFile["Oscilloscope"]["DUT_CHANNEL"].split(",") ]
        self.TriggerChannel = int(configFile["Oscilloscope"]["TRIGGER_CHANNEL"])
        self.TriggerSetting = [int(configFile["Oscilloscope"]["TRIGGER_SETTING_CH"]), str(configFile["Oscilloscope"]["TRIGGER_SETTING_EDGE"]), float(configFile["Oscilloscope"]["TRIGGER_SETTING_TH"]), str(configFile["Oscilloscope"]["TRIGGER_SETTING_MODE"])]
        self.PSChannelList =  [ int(x) for x in configFile["CAEN_PowerSupply"]["ENABLE_CHANNEL"].split(",") ]
        self.PSDUTChannel =  int(configFile["CAEN_PowerSupply"]["DUT_CHANNEL"])
        self.PSTriggerChannel = int(configFile["CAEN_PowerSupply"]["TRIGGER_CHANNEL"])
        self.PSSoftwareCompliance = float(configFile["CAEN_PowerSupply"]["SOFTWARE_COMPLIANCE"])

        self.DAQMasterDir = str(configFile["General_Settting"]["MASTER_PATH"])
        self.DAQDataDir = str(configFile["File_Name"]["PARENT_DIR"])

        self.ThresholdScan_VoltageList = [ int(x) for x in configFile["Edge_Threshold_Scan"]["VOLTAGE_LIST"].split(",") ]
        self.ThresholdScan_MaxEvent = int(configFile["Edge_Threshold_Scan"]["nEvent"])
        self.ThresholdScan_StartValue = float(configFile["Edge_Threshold_Scan"]["Threshold_start"])
        self.ThresholdScan_EndValue = float(configFile["Edge_Threshold_Scan"]["Threshold_end"])
        self.ThresholdScan_Step = float(configFile["Edge_Threshold_Scan"]["Threshold_step"])
        self.ThresholdScan_MaxTime = float(configFile["Edge_Threshold_Scan"]["MAX_TIME"])
        self.ThresholdScan_ScopeChannel = configFile["Edge_Threshold_Scan"]["Channel"]
        self.ThresholdScan_PSChannel = configFile["Edge_Threshold_Scan"]["Power_Channel"]
        self.ThresholdScan_Timeout = float(configFile["Edge_Threshold_Scan"]["Timeout"])
        self.ThresholdScan_FileNameList = []
        for volt in self.ThresholdScan_VoltageList:
            self.ThresholdScan_FileNameList.append( str("Sr_Run"+str(self.RunNumber)+"_"+str(volt)+"V_Ch"+str(self.ThresholdScan_ScopeChannel)))
        print(self.ThresholdScan_FileNameList)

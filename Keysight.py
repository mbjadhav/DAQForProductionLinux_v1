import pyvisa as visa
import time
from time import sleep
import sys
#from LecroyTRCReader import *
import numpy as np
#import matplotlib.pyplot as plt

class KeysightScope(object):
    '''
    Class for Keysight infiniium DSOS204A Oscilloscope
    '''
    active_channels = []

    def __init__(self, ip_address):
        '''
        initial a scope object with ethernet connection.
        '''
        self._model = "KEYSIGHT"
        if not ip_address:
            print("No ip address")
            return
            
        #print(ip_address)
        self.rm=visa.ResourceManager("@py")
        print("Using ethernet connection: ")
        self.inst = self.rm.open_resource("TCPIP0::" + ip_address + "::inst0::INSTR", read_termination='\n', write_termination='\n', chunk_size=1024)
        #self.inst.write("*IDN?;")
        #idn = self.inst.read()
        self.inst.clear()
        self.inst.write("*CLR?;")
        idn = self.inst.query("*IDN?;")
        
        self.default_seg_count = 20

        if "KEYSIGHT" in idn:
            print("\nConnected to Keysight infinium DSOS204A Oscilloscope.\n")
            time.sleep(0.01)
        else:
            print("\nUnable to connect to Keysight infinium DSOS204A Oscilloscope.\n")
            board = 0
            while(True):
                print("\n retrying board {}...".format(board))
                self.inst = visa.ResourceManager("@py").open_resource("TCPIP"+ str(board) +"::" + ip_address + "::inst0::INSTR")
                self.inst.write("*IDN?;")
                idn = self.inst.read()
                if "KEYSIGHT" in idn:
                    print("\nConnected to Keysight infinium DSOS204A Oscilloscope.\n")
                    time.sleep(0.01)
                    break
                else:
                    print("\nStill unable to connect to Keysight infinium DSOS204A Oscilloscope.\n")
                    board += 1
                    #return

        self.inst.timeout =100000

    #===========================================================================
    def _Set_Trigger_Mode(self, channel, mode):
        mode_list = ["TRIGgered", "AUTO", "SINGle", "STOP"]
        if mode in mode_list:
            self.inst.write(":TRIGger:SWEep {}".format(mode))
            self.inst.write(":TRIGger:MODE EDGE")
        else:
            self.inst.write(":TRIGger:SWEep {}".format(mode_list[0]))
        time.sleep(0.01)
        
    #===========================================================================
    def _Set_Trigger_Slope(self, channel, slope):
        slope_list = ["NEGative", "POSitive", "EITHer"]
        if slope in slope_list:
            self.inst.write(":TRIGger:EDGE:SOURce CHANnel{};:TRIGger:EDGE:SLOPe {}".format(channel, slope))
        else:
            #take default [0] if slope is not one of the mode in trig_slope
            self.inst.write(":TRIGger:EDGE:SOURce CHANnel{};:TRIGger:EDGE:SLOPe {}".format(channel, slope_list[0]))
        time.sleep(0.01)
        
    #===========================================================================
    def _Set_Trigger_Level(self, channel, threshold):
        self.inst.write(":TRIGger:LEVel CHANnel{}, {}".format(channel, threshold))
        time.sleep(0.01)

    #***************************************************************************
    def Close(self):
        self.inst.close()

    #***************************************************************************
    
    def reopen_resource(self):
        print("reopen do nothing!")
    
    #===========================================================================
    def Set_Channel_Display(self, channel, switch):
        self.inst.write("CHANnel{}:DISPlay {}".format(channel, switch))

    #===========================================================================
    def Arm_trigger(self, channel_number, slope, threshold, sweep_mode="TRIGgered"):
        self._Set_Trigger_Mode(channel_number, sweep_mode)
        self._Set_Trigger_Slope(channel_number, slope)
        self._Set_Trigger_Level(channel_number, threshold)

    #===========================================================================
    def Create_dir(self, dirc): #dont use it, it is garbage.
        self.inst.write(":DISK:MDIR 'C:\\Users\\KeysightUser\\{}\\'".format(dirc))
        self.inst.write(":DISK:CDIR 'C:\\Users\\KeysightUser\\{}\\'".format(dirc))

    #===========================================================================
    def Set_DAQScope(self):
        self.inst.write(":*CLS")
        self.inst.write(":STOP")
        self.inst.write(":ACQuire:MODE SEGMented") #RTIMe is normal mode of operation
        self.inst.write(":ACQuire:SEGMented:COUNt {}".format(self.default_seg_count) )
        self.inst.write(":ACQuire:BANDwidth MAX")
        self.inst.write(":ACQuire:INTerpolate OFF")
        self.inst.write(":ACQuire:AVERage OFF")
        self.inst.write(":ACQuire:POINts:AUTO ON")
        #self.inst.write(":ACQuire:POINts 50")
        self.inst.write(":ACQuire:COMPlete 100")
        self.inst.write(":WAVeform:FORMAT ASCii")
        self.inst.write(":WAVeform:STReaming ON")
        self.inst.write(":WAVeform:SEGMented:ALL ON")
        self.inst.write("*SRE 7")
        self.inst.write("*SRE 5")
        self.inst.write("*SRE 0")
        self.inst.write(":RUN")

        self.inst.write(":SYST:GUI OFF")

        self.segCount = self.default_seg_count#int(self.inst.query(":WAV:SEGM:COUN?"))
        print("seg count = {}".format(self.segCount))

    #===========================================================================
    def _Get_Waveform_Binary(self, channel, raw=False, seq_mode=False):
        '''
        Get waveform with binary format. Loop through list of channels.
        '''
        
        voltage_list = []
        time_list = []
        raw_data = []
        segmentCount = ""
        waveCount = ""

#In WORD format data is transferred as signed 16bit integers in 2 bytes.
        self.inst.write("*CLS")
        self.inst.write(":WAVeform:FORMAT WORD")
        self.inst.write(":WAVeform:BYTEORDER MSBF") # Set the byte order to Big-Endian (default for Infinium oscilloscopes)
        #self.inst.write(":WAVeform:STReaming 1")
        #self.inst.write(":DIGitize")
        #print("in keysight")
        
        if isinstance(channel, list):
            for ch in channel:
                #self.inst.write(":SYSTem:HEADer OFF")
                self.inst.write(":WAVeform:SOURce CHANnel{}".format(ch))
                #wave_preamble=self.inst.query(":WAVeform:PREamble?")
                #print("set to get waveform")
                self.inst.read_termination ='\n'#None #For binary data it needs to remove the newline read termination
                binary_stream = self.inst.query_binary_values(":WAVeform:DATA?", 'h', is_big_endian = True, container = np.array, expect_termination=False)
                if raw:
                    raw_data.append(binary_stream)
                    continue
                y_inc = float(self.inst.query(":WAVeform:YINC?"))
                y_or = float(self.inst.query(":WAVeform:YOR?"))
                voltage_data = binary_stream*y_inc + y_or
                waveCount = int(self.inst.query(":WAVeform:POINts?")) # Get the number of sample points in the waveform
                #print("waveCount is {}".format(waveCount))
                x_inc = float(self.inst.query(":WAVeform:XINC?")) # Get the waveform's X increment
                x_or = float(self.inst.query(":WAVeform:XOR?")) # Get the waveform's X origin
                time_data = np.linspace(x_or, x_or+(waveCount+1)*x_inc, waveCount) # Calculate the sample times of the waveform
                #horizontal_offset = trcReader(binary_stream, "HORIZ_OFFSET", ch)
                #horizontal_inter = trcReader(binary_stream, "HORIZ_INTERVAL", ch)
                #print("complete taking waveform")
                #print(voltage_data)
                #print(time_data)
                voltage_list.append(voltage_data)
                time_list.append(time_data)
                if seq_mode:
                    segmentCount = self.inst.query(":WAVeform:SEGMented:COUNt?")
            if raw:
                return raw_data
            else:
                if seq_mode:
                    return [time_list, voltage_list, segmentCount, waveCount]
                else:
                    print(time_list)
                    print(voltage_list)
                    return [time_list, voltage_list]
        elif isinstance(channel, int):
            channel_list = []
            channel_list.append(channel)
            return self._Get_Waveform_Binary(channel_list, raw)
        else:
            raise ValueError("Non-supported channel input. Please feed in list of int of single int.")

    #===========================================================================
    def _Get_Waveform_ASCII(self, channel, seq_mode=False):
    
    #Get waveform with ascii format. Loop through list of channels.
 
        
        #self.inst.write(":WAVeform:BYTEORDER MSBF") # Set the byte order to Big-Endian (default for Infinium oscilloscopes)
        #self.inst.write(":WAVeform:FORMAT ASCii")
         
        if isinstance(channel, list):
            voltage_list = []
            time_list = []
            #waveCount = ""
            segmentCount = ""
            splitLevel = 1

            for ch in channel:
                start_pt = 1
                read_pnt = 0
                self.inst.query(":WAVeform:SOURce CHANnel{};*OPC?".format(ch))
                waveCount = int(self.inst.query(":WAVeform:POINts?"))/splitLevel
                read_pnt = waveCount
                voltage_data = []
                
                if self.segCount < 1:
                    wfm_ascii = self.inst.query(":WAVeform:DATA? {},{};*OPC?".format(start_pt, read_pnt)).split(";")[0]
                    #wfm_ascii = wfm_ascii[:-1]
                    wfm_ascii = [float(x) for x in wfm_ascii.split(",")][:-1]
                    voltage_data += wfm_ascii
                else:
                    for seg in range(self.segCount*splitLevel):
                        print("in segment loop {}".format(seg))
                        for splt in range(splitLevel):
                            if splt != splitLevel-2:
                                read_pnt = waveCount
                                print("in splt != splitLevel-2 loop {}".format(splt))
                            else:
                                read_pnt = waveCount + 3
                                print("in splt != splitLevel-2 else loop {}".format(splt))
                            print("wfm_ascii wavecount {} {}".format(waveCount, read_pnt*self.segCount))
			    wfm_ascii_debug = self.inst.query(":WAVeform:DATA? {},{};*OPC?".format(1, read_pnt*self.segCount))
		            print("wfm_ascii debug {}".format(wfm_ascii_debug))
                            with open('wfm_ascii_debug.txt', 'w') as f:
		                f.write(wfm_ascii_debug)
                            wfm_ascii_debug0 = self.inst.query(":WAVeform:DATA? {},{};*OPC?".format(start_pt, read_pnt))
		            print("wfm_ascii debug0 {}".format(wfm_ascii_debug0))
                            with open('wfm_ascii_debug0.txt', 'w') as f:
		                f.write(wfm_ascii_debug0)
			    wfm_ascii = wfm_ascii_debug0.split(";")[0]
                            #wfm_ascii = self.inst.query(":WAVeform:DATA? {},{};*OPC?".format(start_pt, read_pnt)).split(";")[0]
			    print("wfm_ascii debug1 {}".format(wfm_ascii))
                            with open('wfm_ascii_debug_1.txt', 'w') as f:
                                f.write(wfm_ascii)
                            wfm_ascii = wfm_ascii[:-1]
			    print("wfm_ascii debug2 {}".format(wfm_ascii))
                            with open('wfm_ascii_debug_2.txt', 'w') as f:
                                f.write(wfm_ascii)
                            wfm_ascii = [float(x) for x in wfm_ascii.split(',')]
			    print("wfm_ascii debug3 {}".format(wfm_ascii))
                            voltage_data += wfm_ascii
                            print("set to get waveform")
                            if splt != splitLevel-2:
                                start_pt += waveCount
                            else:
                                start_pt += waveCount + 3
                
                time_data = []

                '''
                x_inc = float(self.inst.query(":WAVeform:XINC?")) # Get the waveform's X increment
                x_or = float(self.inst.query(":WAVeform:XOR?")) # Get the waveform's X origin
                time_data = np.linspace(x_or, x_or+(waveCount+1)*x_inc, waveCount) # Calculate the sample times of the waveform
		'''
                voltage_list.append(voltage_data)
                time_list.append(time_data)
            
            #x_inc = float(self.inst.query(":WAVeform:XINCreament?")) # Get the waveform's X increment
            #x_or = float(self.inst.query(":WAVeform:XORigin?")) # Get the waveform's X origin
            x_inc = self.inst.query(":WAVeform:XINCreament?;*OPC?".format(ch)).split(";")[0] # Get the waveform's X increment
            x_or = self.inst.query(":WAVeform:XORigin?;*OPC?".format(ch)).split(";")[0] # Get the waveform's X origin
            last_t = float(x_or)
            for ch, chan in enumerate(voltage_list):
                for i in range(len(chan)):
                    time_list[ch].append(last_t+float(x_inc))
                    last_t += float(x_inc)
            
            #print(len(voltage_list))
            #return [t_output, v_output]
            if seq_mode:
                segmentCount = self.inst.query(":WAVeform:SEGMented:COUNt?")
                return [time_list, voltage_list, segmentCount, waveCount]
            else:
                return [time_list, voltage_list]
        elif isinstance(channel, int):
            channel_list = []
            channel_list.append(channel)
            return self._Get_Waveform_ASCII(channel_list)
        else:
            raise ValueError("Non-supported channel input. Please feed in list of int of single int.")

     #===========================================================================
    def _Get_Waveform_BinaryI(self, channel, seq_mode=False):
    
    #Get waveform with ascii format. Loop through list of channels.
   
    
        voltage_list = []
        time_list = []
        waveCount = ""
        segmentCount = ""
        splitLevel = 1
        
        #self.inst.write(":WAVeform:BYTEORDER MSBF") # Set the byte order to Big-Endian (default for Infinium oscilloscopes)
        self.inst.write(":WAVeform:FORMAT WORD")
        self.inst.write(":WAVeform:BYTEORDER MSBF")
        
        if isinstance(channel, list):
            for ch in channel:
                start_pt = 1
                read_pnt = 0
                self.inst.query(":WAVeform:SOURce CHANnel{};*OPC?".format(ch))
                waveCount = int(self.inst.query(":WAVeform:POINts?"))/splitLevel
                read_pnt = waveCount
                voltage_data = []
                voltage_stream = []
                print("waveCount is {}".format(waveCount))

                if self.segCount < 1:
                    #wfm_ascii = self.inst.query(":WAVeform:DATA? {},{};*OPC?".format(start_pt, read_pnt)).split(";")[0]
                    wfm_ascii = self.inst.query_binary_values(":WAVeform:DATA?;*OPC?", 'h', is_big_endian = True, container = np.array, expect_termination=False)
                    y_inc = float(self.inst.query(":WAVeform:YINC?"))
                    y_or = float(self.inst.query(":WAVeform:YOR?"))
                    voltage_stream = wfm_ascii*y_inc + y_or
                    #wfm_ascii = wfm_ascii[:-1]
                    #wfm_ascii = [float(x) for x in wfm_ascii.split(",")][:-1]
                    voltage_data += voltage_stream
                else:
                    for seg in range(self.segCount*splitLevel):
                        for splt in range(splitLevel):
                            if splt != splitLevel-2:
                                read_pnt = waveCount
                            else:
                                read_pnt = waveCount + 3
                            #wfm_ascii = self.inst.query(":WAVeform:DATA? {},{};*OPC?".format(start_pt, read_pnt)).split(";")[0]
                            wfm_ascii = self.inst.query_binary_values(":WAVeform:DATA?;*OPC?", 'h', is_big_endian = True, container = np.array, expect_termination=False)
			    print("waveCount1 is {}".format(waveCount))
                            
                            #wfm_ascii = wfm_ascii[:-1]
                            #wfm_ascii = [float(x) for x in wfm_ascii.split(",")][:-1]
			    y_inc = float(self.inst.query(":WAVeform:YINC?"))
                            y_or = float(self.inst.query(":WAVeform:YOR?"))
                            voltage_stream = wfm_ascii*y_inc + y_or
                            voltage_data += voltage_stream
                            if splt != splitLevel-2:
                                start_pt += waveCount
                            else:
                                start_pt += waveCount + 3
                
                time_data = []
                
                x_inc = float(self.inst.query(":WAVeform:XINC?")) # Get the waveform's X increment
                x_or = float(self.inst.query(":WAVeform:XOR?")) # Get the waveform's X origin
                time_data = np.linspace(x_or, x_or+(waveCount+1)*x_inc, waveCount) # Calculate the sample times of the waveform
		
                voltage_list.append(voltage_data)
                time_list.append(time_data)
            '''
            x_inc = float(self.inst.query(":WAVeform:XINCreament?")) # Get the waveform's X increment
            x_or = float(self.inst.query(":WAVeform:XORigin?")) # Get the waveform's X origin
            last_t = float(x_or)
            for ch, chan in enumerate(voltage_list):
                for i in range(len(chan)):
                    time_list[ch].append(last_t+float(x_inc))
                    last_t += float(x_inc)
            '''
            #print(len(voltage_list))
            #return [t_output, v_output]
            if seq_mode:
                    segmentCount = self.inst.query(":WAVeform:SEGMented:COUNt?")
                    return [time_list, voltage_list, segmentCount, waveCount]
            else:
                return [time_list, voltage_list]
        elif isinstance(channel, int):
            channel_list = []
            channel_list.append(channel)
            return self._Get_Waveform_BinaryI(channel_list)
        else:
            raise ValueError("Non-supported channel input. Please feed in list of int of single int.")

   #===========================================================================
    def Get_Waveform(self, channel, mode="binary_1", seq_mode=False):
        if "binary" in mode and "raw" in mode:
            try:
                return self._Get_Waveform_Binary(channel, raw=True)
            except ValueError as error:
                print(error)
        elif "binary_1" in mode:
            try:
                return self._Get_Waveform_Binary(channel, False, seq_mode)
            except ValueError as error:
                print(error)
        elif "binary_2" in mode:
            try:
                return self._Get_Waveform_BinaryI(channel, seq_mode)
            except ValueError as error:
                print(error)
        elif "ascii" in mode:
            try:
                return self._Get_Waveform_ASCII(channel, seq_mode)
            except ValueError as error:
                print(error)
        else:
            raise ValueError("Non-supported mode or channels")

    #===========================================================================
    def Wait_For_Next_Trigger(self, timeout = 0.0, trigger_scan = None):
        self.inst.clear()
        self.inst.query("*CLS;*OPC?")
        data  = self.inst.query(":DIGitize;*OPC?")
        return data

    #===========================================================================
    def _test(self):
        self.inst.write(":TRIGger:LEVel CHANnel2, 50")
        self.inst.write(":TRIGger:EDGE:SOURce CHANnel2;:TRIGger:EDGE:SLOPe NEGative")

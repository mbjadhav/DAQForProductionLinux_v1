'''
Scope and Power supply producer
'''

#from DAQConfigReader import *
from Keysight import *
from CAEN_PS import *

class ScopeProducer:
    def __init__(self, configFile ):
        #self._config = DAQConfig()
        #self._config.ReadDAQConfig( configFileName )
        self._config = configFile
        self.Scope = ""

        if "keysight" in self._config.ScopeName:
            print("Keysight scope is produced.")
            self.Scope = KeysightScope( self._config.ScopeIP )
            print("Setting up scope trigger and power supply.")
            
            self.Scope.Arm_trigger( self._config.TriggerSetting[0], self._config.TriggerSetting[1], self._config.TriggerSetting[2], self._config.TriggerSetting[3] )
            print("Enabling scope channels...")
            for ch in self._config.EnableChannelList:
                self.Scope.Set_Channel_Display(ch, "ON")
            self.Scope.Set_DAQScope()

            print("Producing scope methods...")

            def Produce_GetWaveform():
                def GetWaveform( ChannelList, mode="binary", seq_mode=True): #mode binary and ascii
                    data = self.Scope.Get_Waveform(ChannelList, mode, seq_mode) #instead get_ascii_waveform_remote(ChannelList)
                    return data
                return GetWaveform
            self.GetWaveform = Produce_GetWaveform()

            def Produce_WaitTrigger():
                def WaitTrigger(timeout=0.0, trigger_scan=None):  #trigger_scan is declared!
                    status = self.Scope.Wait_For_Next_Trigger(timeout,trigger_scan) #instead waiting_for_next_wave()
                    return status
                return WaitTrigger
            self.WaitForTrigger = Produce_WaitTrigger()

            def Produce_SetTrigger():
                def SetTrigger(Channel, Threshold, Polarity, Mode):
                    self.Scope.Arm_trigger(Channel, Polarity, Threshold, Mode) #also sets acquisition_setting
                    self.Scope.Set_DAQScope()
                return SetTrigger
            self.SetTrigger = Produce_SetTrigger()


class PowerSupplyProducer:
    def __init__(self, configFile ):
        #configParser = DAQConfig()
        #self._config = configParser.ReadDAQConfig( configFileName )
        self._config = configFile
        self.PowerSupply = ""

        self.ConfirmVoltage = ""
        self.SetVoltage = ""
        self.CurrentReader = ""
        self.Close = ""

        if True:
            print("Caen power supply is produced")
            self.PowerSupply = SimpleCaenPowerSupply()
            self.PowerSupply.Set_Compliance( self._config.PSSoftwareCompliance/2.0, self._config.PSSoftwareCompliance/5.0)
            for ch in self._config.PSChannelList:
                self.PowerSupply.channel_switch(ch, "ON")
                voltage_now = self.PowerSupply.voltage_monitor_value(ch,0)
                self.PowerSupply.set_voltage(ch, voltage_now)
            #self.PowerSupply.set_voltage( self._config.PSTriggerChannel, self._config.TriggerVoltage )

            def Produce_ConfirmVoltage():
                def ConfirmVoltage( PS_Channel, TargetVoltage ):
                    return self.PowerSupply.confirm_voltage(PS_Channel, TargetVoltage )
                return ConfirmVoltage
            self.ConfirmVoltage = Produce_ConfirmVoltage()

            def Produce_SetVoltage():
                def SetVoltage( PS_Channel, TargetVoltage ):
                    self.PowerSupply.set_voltage( PS_Channel, TargetVoltage )
                return SetVoltage
            self.SetVoltage = Produce_SetVoltage()

            def Produce_CurrentReader():
                def CurrentReader( PS_Channel ):
                    return self.PowerSupply.current_monitor_value( PS_Channel, 0)
                return CurrentReader
            self.CurrentReader = Produce_CurrentReader()

            def Produce_Close():
                def Close():
                    return self.PowerSupply.close("ALL")
                return Close
            self.Close = Produce_Close()

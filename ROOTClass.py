import ROOT
from array import array

class ROOTFileOutput():
    def __init__(self, fileName, branch_list, opt=None):
        self.tfile = ROOT.TFile( fileName, "RECREATE", "8")
        self.ttree = ROOT.TTree( "wfm", "recorded waveform(remote mode)")
        self.w = []
        self.t = []
        self.i_timestamp = array( "d", [0] )
        self.i_current = array( "d", [0] )
        self.threshold_level = array("d", [0])
        self.additional_branch = dict()

        if opt is None:
            pass
        elif "Threshold_scan" in opt:
            self.ttree.Branch( "threshold_level", self.threshold_level, "threshold_level/D" )
        else:
            pass
        self.ttree.Branch( "i_timestamp", self.i_timestamp, "i_timestamp/D" )
        self.ttree.Branch( "i_current", self.i_current, "i_current/D" )
        for i in range(len(branch_list)):
            self.w.append( ROOT.std.vector("double")() )
            self.t.append( ROOT.std.vector("double")() )
            self.ttree.Branch( "w{}".format(branch_list[i]), self.w[i] )
            self.ttree.Branch( "t{}".format(branch_list[i]), self.t[i] )

    def Fill(self):
        self.ttree.Fill()
        for b in self.w:
            b.clear()
        for b in self.t:
            b.clear()

    def create_branch(self, name, type):
        if type == "D":
            self.additional_branch[str(name)] = array("d", [0])
        elif type == "I":
            self.additional_branch[str(name)] = array("i", [0])
        else:
            print(" >> Invalid data type for {branch}".format(branch=name))
            print(" >> Using default (type Double)")

        self.ttree.Branch(str(name), self.additional_branch[name], "%s/%s"%(name, type) )
        print(" >> additional branch (%s) is created"%name)

    def Close(self):
        print(" >> Writing file")
        self.tfile.Write()
        self.tfile.Close()
        print(" >> file is finished")

class MacroNode:
    def __init__(self):

        #Input
        self.ID = ""                #ID of the macronode
        self.Type = ""              #Type of node (5 choices)
        self.ResID = []             #ID of the reservoir(s) where the node belongs
        self.Capacity = []          #Changes of capacity at each step time
        self.Coord = []             #Abscissa and ordinate of the node




    def load_input(self, loadNetwork, i):
        self.ID = loadNetwork["MACRONODES"][i]["ID"]
        self.Type = loadNetwork["MACRONODES"][i]["Type"]
        self.ResID = loadNetwork["MACRONODES"][i]["ResID"]
        self.Capacity = loadNetwork["MACRONODES"][i]["Capacity"]
        self.Coord = loadNetwork["MACRONODES"][i]["Coord"]

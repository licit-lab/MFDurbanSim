import pandas

def get_macronode(macronodes,macronode_id):
    
    for mn in macronodes:
        if mn.ID==macronode_id:
            return mn
        
    return 0

class MacroNode:
    def __init__(self):

        #Input
        self.ID = ""                #ID of the macronode
        self.Type = ""              #Type of node (5 types: externalentry, externalexit, origin, destination, border)
        self.ResID = []             #ID of the reservoir(s) where the node belongs
        self.Capacities = pandas.DataFrame()            # Capacities (may be dynamic)
        self.Coord = []             #Abscissa and ordinate of the node

    def load_input(self, loadNetwork, i):
        self.ID = loadNetwork["MACRONODES"][i]["ID"]
        self.Type = loadNetwork["MACRONODES"][i]["Type"]
        self.ResID = loadNetwork["MACRONODES"][i]["ResID"]
        
        self.Capacities=pandas.DataFrame.from_dict(loadNetwork["MACRONODES"][i]["Capacity"])
        self.Capacities.set_index('Time')
       
        self.Coord = loadNetwork["MACRONODES"][i]["Coord"]

    def get_capacity(self, time):
        return self.Capacities.loc[:time].tail(1).Data[0]
    
    
    

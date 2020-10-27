import pandas

def get_macronode(macronodes,macronode_id):
    
    for mn in macronodes:
        if mn.ID == macronode_id:
            return mn
        
    return None

class MacroNode:

    macronode_types_list = ("externalentry", "border", "origin", "destination", "externalexit")

    def __init__(self):
        #Input
        self.ID = ""                #ID of the macronode
        self.Type = ""              #Type of node (5 types: externalentry, externalexit, origin, destination, border)
        self.ResID = []             #ID of the reservoir(s) where the node belongs
        self.Capacities = pandas.DataFrame()            # Capacities (may be dynamic)
        self.Coord = []             #Abscissa and ordinate of the node

    def load_input(self, loadNetwork, i):
        network = loadNetwork["MACRONODES"][i]

        self.ID = network["ID"]

        if network["Type"] in self.macronode_types_list:
            self.Type = network["Type"]
        else:
            print("Type of macro node unknown, please change the input file entry Type.")

        self.ResID = network["ResID"]
        
        if 'Capacity' in network:
            self.Capacities = pandas.DataFrame.from_dict(network["Capacity"])
            self.Capacities.set_index('Time')
       
        if 'Coord' in network:
            self.Coord = network["Coord"]

    def get_capacity(self, time):
        if self.Capacities.size == 0:
            return 1.
        return self.Capacities.loc[:time].tail(1).Data[0]
    
    
    

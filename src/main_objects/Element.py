class Element:
    
    def __init__(self, datakeys):
        self.Data = []
        self.DataKeys= datakeys
        
    def init_time_step(self, t):
        
        data = dict(zip(self.DataKeys, [0]*len(self.DataKeys)))
        data['time']=t
        
        self.Data.append(data)
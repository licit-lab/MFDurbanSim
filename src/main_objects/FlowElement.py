class FlowElement:
    """
    A class used to represent the dynamic variables of a multi-modal flow element class

    ...

    Attributes
    ----------
    modes : list of str
        list of label to define the used modes
    FlowData : list of nested dictionnaries
        dynamic variables
    FlowDataKeys : list of str
        list of dynamic variables label
    
    Methods
    -------
    init_time_step(timestep)
        initializes a new time step
    """
    
    def __init__(self, datakeys, modes):
        """
        Parameters
        ----------
        modes : list of str, optional
            list of label to define the used modes
        """

        self.FlowData = []
        self.FlowDataKeys= ['Time'] + datakeys
        self.modes = modes
        
    def init_time_step(self, timestep):
        """
        Initializes a new time step

        Parameters
        ----------
        timestep : float
            timestep (in seconds) to initialize
        """
        
        d=dict(zip(self.modes,[0.0]*len(self.modes)))
        #d = {'VL':0.0}
        data = dict(zip(self.FlowDataKeys, [timestep]+[d]*(len(self.FlowDataKeys)-1)))
        #data = {'Time':timestep,'Acc':d}
       
        self.FlowData.append(data)
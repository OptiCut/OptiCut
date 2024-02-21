class Observer(object):
    '''Class that holds all of the observation functions of the parts in any given fusion 360 file.'''
    

    def getLength(Self, Part):
        # getLength(Part) is used to get the length of a part from file. Retruning the parts Length as a float.
        pass
    
    def getWidth(Self, Part):
        # getWidth(Part) is used to get the width of a part from file. Returning the parts width as a float.
        pass
    
    def getDepth(Self, Part):
        # getDepth(Part) is used to get the depth of a part from file. Returning the part's hight as a float.
        pass
    
    def getPartCount(Self, Part_Table):
        # getPartCount(Part_Table) is used to get a count of all parts in the parts table. Retruning the part count as a int.
        pass
    
    def generatePartTable(Self):
        # generatePartTable() is used to get a table of every part and their variables for callable access.
        pass
    
    def getPart(Self, Part, Variable):
        # getPart(Part) is used to get all variables or a single variable of a part from the part table. Returning the part's
        # variable/s as a float list.
        pass
    
    pass





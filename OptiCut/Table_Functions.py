class Table_Functions(object):
    '''Class that holds all of the observation functions of the parts and table holding the workable data in any given fusion 360 file.'''
    
    def __init__(self):
        # When starting the observer object it initates a couple of callable variables for stroing the data of each of the parts.
        self.part_table = {}
        
    def getLength(self, part):
        # getLength(Part) is used to get the length of a part from file. Retruning the parts Length as a float.
        pass
    
    def getWidth(self, part):
        # getWidth(Part) is used to get the width of a part from file. Returning the parts width as a float.
        pass
    
    def getDepth(self, part):
        # getDepth(Part) is used to get the depth of a part from file. Returning the part's hight as a float.
        pass
    
    def getPartCount(self, part_Table):
        # getPartCount(Part_Table) is used to get a count of all parts in the parts table. Retruning the part count as a int.
        pass
    
    def generatePartTable(self):
        # generatePartTable() is used to get a table of every part and their variables for callable access.
        pass
    
    def getPart(self, part, variable):
        # getPart(Part) is used to get all variables or a single variable of a part from the part table. Returning the part's
        # variable/s as a float list.
        pass
    
    pass





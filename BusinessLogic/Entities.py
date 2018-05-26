class NavItem:

    def __init__(self , displayName , link):
        self.Display = displayName
        self.Link = link

class DataFilter:

    def __init__(self,dfColIndex , op , value):
        self.dfColIndex = dfColIndex
        self.op = op
        self.value = value
import pandas as pd

from collections import defaultdict

class StatOps:

    cum_mean = 'CumulativeMean'
    mean = "Mean"

    @staticmethod
    def HandleOp(statop,op,args):
        #print(op,args)
        method_name = getattr(StatOps , op.lower())
        method = getattr(statop , method_name)
        return method(*args) if len(args) >= 1 else method()

    def __init__(self, dataframe):

        self.dataframe = dataframe
        self.applied_ops = defaultdict(list)

    def IsApplied(self,op,col):
        if op in self.applied_ops and col in self.applied_ops[op]:
            return True
        return False

    def Mean(self,col,keyCol):
        import BusinessLogic.Mapping as BLM
        self.applied_ops[StatOps.mean].append(col)

        col = BLM.GetCol(self.dataframe , col)
        keyCol = BLM.GetCol(self.dataframe , keyCol)

        rowToAdd = pd.DataFrame([[self.dataframe[col].mean() , StatOps.mean]] ,columns=[col , keyCol])
        #return pd.DataFrame([[self.dataframe[col].mean() , StatOps.mean]] ,columns=[col , keyCol])
        self.dataframe = self.dataframe.append(rowToAdd , ignore_index=True, sort=False)
        return self.dataframe

    def CumulativeMean(self, col):
        import BusinessLogic.Mapping as BLM
        col = BLM.GetCol(self.dataframe , col)
        self.dataframe[StatOps.CUM_MEAN] =  self.dataframe[col].expanding().mean()
        return self.dataframe

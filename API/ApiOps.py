import os
import json
import pandas as pd
from pandas.api.types import is_string_dtype,is_numeric_dtype
import numpy as np
import re


def APIFormatJsonToDF(jsonData):
    #columns = [ f['name'].lower() for f in jsonData['field']]
    data = jsonData['records']
    data =  [{k.lower(): v for k, v in d.items()} for d in data]
    columns = [key for key in data[0].keys()]

    df = pd.DataFrame(data = data , columns = columns)
    #print(data ,df,columns)
    return df


def FindColumns(dataframe):
    x,y = "" , ""
    for column in dataframe.columns:
        if is_string_dtype(dataframe[column]):
            y = column
        if is_numeric_dtype(dataframe[column]):
            x = column

    return x,y

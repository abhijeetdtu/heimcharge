import os
import json
import pandas as pd
import numpy as np

import locale
from locale import atof

def GetColumnsFromFile(file):
    jsonData = json.load(open(file))
    return [ f['label'] for f in jsonData['fields']]

def GetFromIDFieldJson(jsonData):
    columns = [ f['label'] for f in jsonData['fields']]
    data = jsonData['data']
    df = pd.DataFrame(data = data , columns = columns)
    return df 

def GetFromCSVLikeJson(jsonData):
    columns = jsonData[0]
    data = jsonData[1:]
    df = pd.DataFrame(data = data , columns = columns)
    return df 

def GetStateColumnFromFile(filename):
    df,columns = GetDataFrame(filename)
    stateColumn = GetStateColumn(df)
    print(filename , stateColumn)
    if stateColumn == None:
        return 0
    return stateColumn[1]

def GetStateColumn(df):

    states= ['andhra pradesh', 'arunachal pradesh', 'assam', 'bihar', 'chhattisgarh', 'goa', 'gujarat', 'haryana', 'himachal pradesh', 'jammu & kashmir', 'jharkhand', 'karnataka', 'kerala', 'madhya pradesh', 'maharashtra', 'manipur', 'meghalaya', 'mizoram', 'nagaland', 'odisha', 'punjab', 'rajasthan', 'sikkim', 'tamil nadu', 'telangana', 'tripura', 'uttar pradesh', 'uttarakhand', 'west bengal', 'total (states)', 'a & n islands', 'chandigarh', 'd&n haveli', 'daman & diu', 'delhi ut', 'lakshadweep', 'puducherry', 'total (uts)', 'total (all india)']

    try:
        for i,column in enumerate(df.columns):
            values = list(df[column].str.lower())
            if len(set(states).intersection(set(values))) > 10:
                return [column,i]
    except:
        pass

    return None

def TypeCheckColumns(df):
     
     stateColumn = GetStateColumn(df)

     for column in list(df.columns):
         
         if stateColumn != None and column == stateColumn[0]:
             df[column] = df[column].str.title()

         try:
            df[column] = df[column].str.replace("NA","0")
            df[column] = df[column].str.replace(",","").astype(float)
            

         except:
             pass
    
     df = df.fillna(0)
     return df

def GetDataFrameFromJson(file , transform = None):
     jsonData = json.load(open(file))

     try:
         df = GetFromIDFieldJson(jsonData)
     except:      
         df = GetFromCSVLikeJson(jsonData)
     
     df = TypeCheckColumns(df)

     if transform != None:
        df = transform(df)

     return df


def GetDataFrame(filename):
    dataFile = os.path.abspath(os.path.join("Data" , filename+".json"))
    df = GetDataFrameFromJson(dataFile)
    columns =list(df.columns)
    return [df ,columns]

def GetFileList(type):
    files = os.listdir(os.path.abspath(os.path.join("." , 'Data')))
    selectedFiles = [f for f in files if f.endswith('.'+type)]
    return selectedFiles

def GetStateWiseFileList(type):
    files = GetFileList(type)
    selectedFiles = [f for f in files if f.lower().find("statewise") >= 0]
    return selectedFiles
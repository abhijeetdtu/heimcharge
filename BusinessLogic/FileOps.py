import os
import json
import pandas as pd
import numpy as np
import re

import locale
from locale import atof

from BusinessLogic.ExceptionHandling import HandleException
import API.ApiOps as ApiOps



def MakeTextSafe(value):
    value = str(value)
    value.replace("'" , "''")
    return value

def ExtractNumbers(value):
    value = str(value)
    try:
        values = re.findall("[\d,]+" ,value)
        values = [value.replace("," , "") for value in values]
    except:
        values = re.findall("[\d.]+" ,value)

    if(values and len(values) > 0):
        try:
            val =  float(values[0])
        except:
            val = 0

        return val


    return 0

def GetColumnsFromFile(file):
    jsonData = json.load(open(file ,  encoding='utf-16'))
    return [ f['label'] for f in jsonData['fields']]

def GetFromIDFieldJson(jsonData):
    try:
        df = FileFormatJsonToDF(jsonData)
    except:
        df = ApiOps.APIFormatJsonToDF(jsonData)

    return df

def FileFormatJsonToDF(jsonData):
    columns = [ f['label'] for f in jsonData['fields']]
    data = jsonData['data']
    df = pd.DataFrame(data = data , columns = columns)
    #print(df)
    return df

def GetFromCSVLikeJson(jsonData):
    columns = jsonData[0]
    data = jsonData[1:]
    df = pd.DataFrame(data = data , columns = columns)
    return df

def GetStateColumnFromFile(filename):
    df,columns = GetDataFrame(filename)
    stateColumn = GetLocationColumn(df, isOnlyState=True)
    #print(filename , stateColumn)
    if stateColumn == None:
        return 0
    return stateColumn[1]

def AreColumnsMatching(df,col ,arr ):
    try:
        values = list(df[col].str.lower())
        if len(set(arr).intersection(set(values))) > len(set(values))/2:
            return True
        return False
    except:
        return False

def GetLocationColumn(df,isOnlyState=False,isOnlyCity=False):
    try:
        for i,column in enumerate(df.columns):
            if isOnlyCity == False:
                val = GetStateColumn(df, column)
                if val != None:
                    return [val,i]
            if isOnlyState == False:
                val = GetCityColumn(df,column)
                if val != None:
                    return [val , i]
    except Exception as e:
        HandleException(e)
    return None

def GetCityColumn(df , column):
    cities = ["delhi" , "mumbai" , "bengaluru" , "chennai" , "kolkata" , "coimbatore" , "ahmedabad" , "jaipur "]
    if AreColumnsMatching(df, column , cities):
        return column
    return None

def GetStateColumn(df , column):
    states= ['andhra pradesh', 'arunachal pradesh', 'assam', 'bihar', 'chhattisgarh', 'goa', 'gujarat', 'haryana', 'himachal pradesh', 'jammu & kashmir', 'jharkhand', 'karnataka', 'kerala', 'madhya pradesh', 'maharashtra', 'manipur', 'meghalaya', 'mizoram', 'nagaland', 'odisha', 'punjab', 'rajasthan', 'sikkim', 'tamil nadu', 'telangana', 'tripura', 'uttar pradesh', 'uttarakhand', 'west bengal', 'total (states)', 'a & n islands', 'chandigarh', 'd&n haveli', 'daman & diu', 'delhi ut', 'lakshadweep', 'puducherry', 'total (uts)', 'total (all india)']
    if AreColumnsMatching(df, column , states):
        return column
    return None

def DigitRatioInString(str):
    return len(re.findall("\d"))/len(str)

def TypeCheckColumns(df):

     stateColumn = GetLocationColumn(df , isOnlyState=True)

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

def GetJSONFromFileOrObj(file):
    if type(file) == str:
        jsonData = json.load(open(file))
    else:
        jsonData = file
    return jsonData

def GetDataFrameFromJson(file , transform = None):

    jsonData = GetJSONFromFileOrObj(file)
    #print(jsonData)
    try:
        df = GetFromIDFieldJson(jsonData)
    except:
        df = GetFromCSVLikeJson(jsonData)

    df = TypeCheckColumns(df)

    if transform != None:
        df = transform(df)

    return df

def ColumnCleanup(df):

    if('S. No.' in df.columns):
        df = df.drop(columns = ['S. No.'])

    return df

def GetDataFrame(filename):
    from API.RestBase import Rest as RT
    
    if filename in RT.GetAllAvailableResources():
        print(filename)
        df = RT.Get(filename , {})
        return [df,df.columns]

    dataFile = os.path.abspath(os.path.join("Data" , filename+".json"))
    df = GetDataFrameFromJson(dataFile)

    df = ColumnCleanup(df)
    columns =list(df.columns)
    return [df ,columns]

def ConvertFileNameToMeaningful(file):
    file = file.split(".")[0]
    regex = "([A-Z]+[a-z]*)"
    return " ".join(re.findall(regex , file))

def GetFileList(type):
    files = os.listdir(os.path.abspath(os.path.join("." , 'Data')))
    selectedFiles = [f for f in files if f.endswith('.'+type)]
    return selectedFiles

def GetStateWiseFileList(type):
    files = GetFileList(type)
    selectedFiles = [f for f in files if f.lower().find("statewise") >= 0 or f.lower().find("locationwise") >= 0]
    return selectedFiles

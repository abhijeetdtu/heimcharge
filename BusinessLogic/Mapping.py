import os
import operator
import re

import json

from flask import Markup

import plotly.plotly as py
from plotly import tools
from plotly.offline import plot

import plotly.graph_objs as go

import folium
import branca.element
import branca.colormap as cm
from branca.utilities import split_six
import pandas as pd

from config import plotting

from BusinessLogic.FileOps import *
from BusinessLogic.IndiaMap import IndiaMapModel
from BusinessLogic.Entities import DataFilter

class ChartBuilderBase:

    def __init__(self ,dataFrame, layoutConfig = None):
        self.DataFrame = dataFrame
        self.layoutConfig = layoutConfig
        print(self.layoutConfig)
        if 'locked' in self.config and 'filters' in self.config['locked']:
            x = [self.AddFilterTransform(filter.dfColIndex , filter.op , filter.value) for filter in self.config['locked']['filters']]


    #to be overriden by child
    def GetChartTrace():
        return []

    def AddFilterTransform(self,dfColIndex ,op, value):
        rowIndices = []
        if type(dfColIndex) == str:
            col = dfColIndex
        else:
            col = self.DataFrame.columns[dfColIndex]
        
        df =self.DataFrame
        print(df[col].head() , op , value,col)

        if op == '==':
            df = df[df[col] == value]
        if op == '>':
            value = float(value)
            df = df[df[col] > value]
        if op == '<':
            value = float(value)
            df= df[df[col] < value]
        if op == '!=':
            df= df[df[col] != value]

        self.DataFrame = df
        #self.DataFrame = self.DataFrame[rowIndices]
    

    def PrepareFigure(self,layoutConfig , traceArr):
        margin=go.Margin(
            b=10,
            t=50,
            pad=4
        )   
        layoutConfig["margin"] = margin
        layout = go.Layout( **layoutConfig)
        figure = go.Figure(data = traceArr , layout = layout)

        return figure

    def GetChart(self):
        if('locked' in self.config):
            del self.config['locked']

        data = self.GetChartTrace()
        return self.PrepareFigure(self.layoutConfig, data)

    def GetChartHTML(self):
        return Markup(self.Plot(self.GetChart()))

    def Plot(self,figure):
        return plot(figure, output_type='div' , config={'displayModeBar': False} , include_plotlyjs=False , validate=False)

class Chart(ChartBuilderBase):

    def __init__(self, goType, dataFrame , xCol , yCol , config):

        layoutConfig = self.SeparateLayoutConfig(config, xCol , yCol )
        self.Xcol =xCol
        self.Ycol = yCol
        self.goType = goType
        self.config = config
        super(Chart, self).__init__(dataFrame,layoutConfig)
        
    def SeparateLayoutConfig(self,config, xCol , yCol):
        if "layoutConfig" in config:
            layoutConfig = config["layoutConfig"]
            if("xaxis" in layoutConfig):
                layoutConfig["xaxis"]["title"] = xCol
            else:
                layoutConfig["xaxis"] = dict(title=xCol)
            if("yaxis" in layoutConfig):
                layoutConfig["yaxis"]["title"] = yCol
            else:
                layoutConfig["yaxis"] = dict(title=yCol)
            del config["layoutConfig"]
        else:
            layoutConfig = dict(xaxis = dict(title=xCol) , yaxis = dict(title = yCol))

        return layoutConfig

    def GetChartTrace(self):    
        return [self.goType(x = self.DataFrame[self.Xcol] , y = self.DataFrame[self.Ycol] ,  **self.config)]

class SingleAxisChart(Chart):
    def __init__(self,goType, dataFrame , col ,axis, config):
        self.axis = axis
        super(SingleAxisChart, self).__init__(goType, dataFrame,col , None , config)
        self.HandleChartSepecific()
    
    def HandleChartSepecific(self):
        if self.goType == go.Histogram:
            bin = dict(start = self.DataFrame[self.Xcol].min() , end = self.DataFrame[self.Xcol].max() , size =self.DataFrame[self.Xcol].std()*self.DataFrame[self.Xcol].mean())
            self.config["{0}bin".format(self.axis)] = bin
                
    def GetChartTrace(self):
        if self.axis == 'y':
            return [self.goType(y=self.DataFrame[self.Xcol])]
        if self.axis == 'x':
            return [self.goType(x=self.DataFrame[self.Xcol])]


class StackedBar(ChartBuilderBase):

    def __init__(self, dataFrame , selectedXColArr , yCol , config):
        layoutConfig= dict(xaxis = dict(title="X-axis") , yaxis = dict(title = yCol),barmode='stack')

        self.SelectedXColArr = selectedXColArr
        self.Ycol = yCol
        self.config = config

        super(StackedBar, self).__init__(dataFrame,layoutConfig)

    def GetChartTrace(self):
        traces= []
        for xcol in self.SelectedXColArr:
            self.config["name"] = xcol
            traces.append(go.Bar(x = self.DataFrame[xcol] , y = self.DataFrame[self.Ycol] ,  **self.config))
        return traces

class Pie(ChartBuilderBase):

    def __init__(self,title, values , labels,config):
        layoutConfig= dict(title = title , xaxis = dict(title="X-axis") , yaxis = dict(title = "Y-Axis"))
        self.Values= values
        self.Lables = labels
        self.config = config

        super(Pie, self).__init__(pd.DataFrame(columns=self.Labels , data=self.Values),layoutConfig)

    def GetChartTrace(self):
        return [go.Pie(values = self.Values , labels = self.Lables ,  **self.config)]

    @staticmethod
    def GetMultiplePieChartsHTML(dataFrame ,selectedXColArr,yCol , config):
        unqValues = dataFrame[yCol].unique()
        return [ Pie(value  , dataFrame[selectedXColArr].values[dataFrame[yCol] == value][0] , selectedXColArr, config).GetChartHTML() for i , value  in enumerate(unqValues)]

class Table():

    def __init__(self,dataFrame):
        self.DataFrame = dataFrame

    def GetTableTrace(self):
        df = self.DataFrame 
        values = [df[col] for i,col in enumerate(df.columns)]
        trace = go.Table(
            header=dict(values=df.columns,
                fill = dict(color='#C2D4FF'),
                align = ['left'] * 5),
        cells=dict(values=values,
               fill = dict(color='#F5F8FF'),
               align = ['left'] * 5))

        return trace
    
    def GetChart(self):
        data = [self.GetTableTrace()]

        figure = go.Figure(data = data)

        return figure

    def GetChartHTML(self):
        return Markup(self.Plot(self.GetChart()))

    def Plot(self,figure):
        return plot(figure, output_type='div' , config={'displayModeBar': False} , include_plotlyjs=False)

def Plot(figure):
    return plot(figure, output_type='div' , config={'displayModeBar': False} , include_plotlyjs=False)

def PopulationTransform(df):   
     df["Population 2011"] = df["Population 2011"].astype(float)
     return df

def BarChartTrace(df , xCol , yCol , orientation = 'h'):
    return go.Bar(
            x=df[xCol], # assign x as the dataframe column 'x'
            y=df[yCol],
            orientation = orientation
        )

def BarChartRaw(df , xCol , yCol , orientation = 'h'):
    data = [
        BarChartTrace(df , xCol , yCol , orientation)
    ]

    layout = go.Layout( xaxis = dict(title=xCol) , yaxis = dict(title = yCol))
    figure = go.Figure(data = data , layout = layout)

    return figure

def BarChart(df , xCol , yCol , orientation = 'h'):
    figure = BarChartRaw(df , xCol , yCol , orientation = 'h')
    return Plot(figure)


def SharedXAxisLayout(chartArr,subplotTitles):

    fig = tools.make_subplots(rows=len(chartArr), cols=1, shared_xaxes=True, shared_yaxes=False  , subplot_titles=tuple(subplotTitles))
    for i,chart in enumerate(chartArr):
        fig.append_trace(chart,i+1,1)

    return fig

def SharedYAxisLayout(chartArr,subplotTitles):
    
    fig = tools.make_subplots(rows=1, cols=len(chartArr), shared_xaxes=False, shared_yaxes=True  , subplot_titles=tuple(subplotTitles))
    for i,chart in enumerate(chartArr):
        fig.append_trace(chart,1,i+1)

    return fig

def SharedBothAxisLayout(chartArr,subplotTitles):
    
    fig = tools.make_subplots(rows=1, cols=1, shared_xaxes=True, shared_yaxes=True  , subplot_titles=tuple(subplotTitles[0]))
    for i,chart in enumerate(chartArr):
        fig.append_trace(chart,1,1)

    return fig

def SharedAxisLayout(chartArr , sharedX , sharedY,subplotTitles):
    if sharedX and sharedY:
        return SharedBothAxisLayout(chartArr , subplotTitles)
    elif sharedX == True:
        return SharedXAxisLayout(chartArr,subplotTitles)
    else:
        return SharedYAxisLayout(chartArr,subplotTitles)

def SharedAxisBarCharts(chartArr , subplotTitles , chartTitle , sharedX , sharedY):
    #fig = SharedAxisLayout(chartArr , sharedX , sharedY,subplotTitles)
    layout = go.Layout( xaxis = dict(title="asd") , yaxis = dict(title = "zxc") , yaxis2= dict(title = "hulu"))
    figure = go.Figure(data = chartArr , layout = layout)
    #fig['layout'].update(showlegend=False, title=chartTitle)
    return Plot(figure)


def UpdateSizeByColorByColumns(df,xCol , yCol ):
    sizeBy = (df[df.columns[xCol]].astype(float).values - df[df.columns[yCol]].astype(float).values)
        
    colorBy = [ 'rgb(255, 144, 14)' if x < 0 else 'rgb(44, 160, 101)' for x in sizeBy]

    sizeBy = (sizeBy-sizeBy.mean())/sizeBy.std()


    sizeBy = list(map(lambda x: abs(x)*50, sizeBy))
    df["sizeBy"] = sizeBy
    df["colorBy"] = colorBy

    return df

def GetMappedValue(OldValue , OldMin , OldMax , NewMax , NewMin):
    return (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin

def GetScatterChart(filename,xCol , yCol , textCol,configBase):
    df,columns = GetDataFrame(filename)
    df = UpdateSizeByColorByColumns(df,xCol , yCol )

    config = dict(mode ='markers+text' , text = df[df.columns[textCol]], marker = dict(size=  df["sizeBy"] , color = df["colorBy"], line = dict(width = 2,)))

    for key in configBase:
        config[key] = configBase[key]

    #print(config)
    return Chart(go.Scatter,df , df.columns[xCol] ,  df.columns[yCol] , config)

def GetChartHTML(filename , xAxis , yAxis ,xaxisPlot='x1', yaxisPlot = 'y1'):
    df,columns = GetDataFrame(filename)
    return Chart(go.Bar , df , columns[xAxis] , columns[yAxis]  , dict(xaxis = xaxisPlot , yaxis = yaxisPlot)).GetChartHTML()

def GetChartTrace(filename , xAxis , yAxis ,xaxisPlot='x1', yaxisPlot = 'y1'):
    df,columns = GetDataFrame(filename)
    return Chart(go.Bar , df , columns[xAxis] , columns[yAxis]   , dict(xaxis = xaxisPlot , yaxis = yaxisPlot)).GetChartTrace()[0]

def GetConfig(request):
    config = dict(locked = dict())
    GetFiltersIntoConfig(request , config)
    return config

def GetFiltersIntoConfig(request , config):
    filterArr = request.args.getlist('filter')
    filters= GetFilterArrayFromArguments(filterArr)
    config["locked"]["filters"] = filters

def GetFilterArrayFromArguments(filterArr):
    filters= []
    for filter in filterArr:
        try:
            colIndex , op , value = re.split("(\d+)([=\!<>]{1,2})(.+)" , filter)[1:-1]
            filters.append(DataFilter(int(colIndex) , op , value))
        except:
            colIndex , op , value = re.split("(\w+)([=\!<>]{1,2})(.+)" , filter)[1:-1]
            filters.append(DataFilter(colIndex , op , value))

    return filters

    

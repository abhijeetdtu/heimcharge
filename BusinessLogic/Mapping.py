import os
import operator
import re
import pdb
import json
import random
import math
import sys
from enum import Enum
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
import numpy as np
import copy

from config import plotting

import BusinessLogic.ExceptionHandling as EX
from BusinessLogic.FileOps import *
from BusinessLogic.IndiaMap import IndiaMapModel
from BusinessLogic.Entities import DataFilter
from BusinessLogic.StatOps import StatOps

selectedScheme = plotting["SelectedScheme"]

class ChartBuilderBase:

    def __init__(self ,dataFrame, layoutConfig = {} , fig = None):
        #pdb.set_trace()
        self.DataFrame = dataFrame
        self.layoutConfig = copy.deepcopy(layoutConfig)
        self.statOps = StatOps(self.DataFrame)
        self.fig = fig

        if 'locked' in self.config and 'transpose' in self.config['locked']:
            self.DataFrame.index = self.DataFrame.index.astype(str)
            self.DataFrame = self.DataFrame.T
            #pdb.set_trace()
            self.DataFrame = self.DataFrame.rename(columns=self.DataFrame.iloc[0].astype(str))
            self.DataFrame = self.DataFrame.drop(self.DataFrame.index[0])
            self.DataFrame["T"] = self.DataFrame.index

        if 'locked' in self.config and 'statops' in self.config['locked']:
            self.DataFrame = self.HandleStatOps(self.config['locked']['statops'])

        if 'locked' in self.config and 'filters' in self.config['locked']:
            [self.AddFilterTransform(filter.dfColIndex , filter.op , filter.value) for filter in self.config['locked']['filters']]

        if 'locked' in self.config and 'sortby' in self.config['locked']:
            col,dataType = self.config['locked']['sortby']
            self.SortBy(col,dataType)

        self.ClenseConfig()

    def UpdateFigure(self):
        pass

    def GetCol(self , dfColIndex):
        try:
            col = self.DataFrame.columns[int(dfColIndex)]
        except:
            col = dfColIndex
        return col

    #to be overriden by child
    def GetChartTrace(self):
        if('locked' in self.config):
            del self.config['locked']

    def SortBy(self,col,dataType):
        col = self.GetCol(col)
        df = self.DataFrame
        if dataType == 'date':
            df[col] = pd.to_datetime(df[col] , errors='ignore')

        df = df.sort_values(col)

        if dataType == 'date':
            df[col] = df[col].dt.strftime('%B %d, %Y, %r')

        self.DataFrame = df

    def AddFilterTransform(self,dfColIndex ,op, value):

        if type(dfColIndex) == str:
            col = dfColIndex
        else:
            col = self.DataFrame.columns[dfColIndex]

        df =self.DataFrame

        #pdb.set_trace()
        if op == '==':
            df = df[df[col] == value]
        if op == '>':
            value = float(value)
            df = df[df[col].astype(float) > value]
        if op == '<':
            value = float(value)
            df= df[df[col].astype(float) < value]
        if op == '!=':
            df= df[df[col] != value]

        self.DataFrame = df
        #self.DataFrame = self.DataFrame[rowIndices]

    def HandleStatOps(self, ops):
        for op,args in ops:
            self.DataFrame = StatOps.HandleOp(self.statOps,op,args)

        return self.DataFrame

    def PrepareFigure(self,layoutConfig , traceArr):

        if "margin" not in layoutConfig:
            margin=go.Margin(
                l=100,
                r=0,
                b=50,
                t=0,
                pad=4
            )
            layoutConfig["margin"] = margin
        layoutConfig["autosize"] = True
        layoutConfig["barmode"]='group'
        layoutConfig["hovermode"]='closest'
        layoutConfig["paper_bgcolor"]='rgba(0,0,0,0)'

        layout = go.Layout(**layoutConfig )
        figure = go.Figure(data = traceArr , layout = layout)
        self.fig = figure

        self.UpdateFigure()
        return self.fig

    def ClenseConfig(self):
        if 'returnPartial' in self.config:
            del self.config['returnPartial']

    def GetChart(self):
        data = self.GetChartTrace()
        return self.PrepareFigure(self.layoutConfig, data)

    def GetChartHTML(self):
        #pdb.set_trace()
        return Markup(self.Plot(self.GetChart()))

    def Plot(self,figure):
        #print(figure)
        return plot(figure, output_type='div' , config={'displayModeBar': False} , include_plotlyjs=False , validate=False)

class Chart(ChartBuilderBase):

    def GetGoType(self,goType):
        if goType.lower() == "bar":
            return "Bar"
        if goType.lower() == "scatter":
            return "Scatter"
        if goType.lower() == "pie":
            return "Pie"
        return goType

    def __init__(self, goType, dataFrame , xCol , yCol , config):
        #pdb.set_trace()
        self.config = copy.deepcopy(config)
        self.config['marker'] = config.get("marker" , dict())

        layoutConfig = self.SeparateLayoutConfig(self.config, xCol , yCol )

        super(Chart, self).__init__(dataFrame,layoutConfig)

        self.Xcol = self.GetCol(xCol)
        self.Ycol = self.GetCol(yCol)

        self.goType = getattr(go , self.GetGoType(goType))

        self.SetupTextAndColors()

    def _quantiles(self,col,colorCol):
        try:
            if 'disableQuantileSort' not in self.config['locked']:
                self.DataFrame = self.DataFrame.sort_values(by=col)

            quantiles = self.DataFrame[col].quantile([0.25 , 0.5 , 0.75 , 1]).values

            self.DataFrame[colorCol] = plotting["ColorSchemes"][selectedScheme][0]
            self.DataFrame.loc[self.DataFrame[col] > quantiles[0], colorCol] = plotting["ColorSchemes"][selectedScheme][1]
            self.DataFrame.loc[self.DataFrame[col] > quantiles[1], colorCol] = plotting["ColorSchemes"][selectedScheme][2]
            self.DataFrame.loc[self.DataFrame[col] > quantiles[2] , colorCol] = plotting["ColorSchemes"][selectedScheme][3]
            self.config['marker']['color'] = self.DataFrame[colorCol]


        except Exception as e:
            EX.HandleException(e)
            pass

    def _markerAndText(self,colorCol):
        try:
            if 'textCol' in self.config['locked']:
                self.config['text'] = self.DataFrame[self.config['locked']['textCol']]

            if 'sizeCol' in self.config['locked']:
                df = self.DataFrame
                col = self.config['locked']['sizeCol']
                normalizedColValues = ((df[col]-df[col].min())/(df[col].max()-df[col].min()) * 50) + 20
                self.config['marker']['size'] =normalizedColValues
        except:
            self.config['marker'] = dict(color =  plotting["ColorSchemes"]["Blueiss"][0])

    def _statopColors(self,col,keyCol,colorCol):
        try:
            if self.statOps.IsApplied(StatOps.mean , col):
                self.DataFrame.loc[self.DataFrame[keyCol] == StatOps.mean , colorCol] = plotting["StatColors"][selectedScheme][StatOps.mean]
        except:
            pass


    def SetupTextAndColors(self):
            col = self.Xcol if (self.DataFrame[self.Xcol].dtype == "float64" or self.DataFrame[self.Xcol].dtype == "int64") else self.Ycol
            keyCol = self.Xcol if col == self.Ycol else self.Ycol
            colorCol = 'MarkerColor' + col
            self._quantiles(col,colorCol)
            self._statopColors(col,keyCol,colorCol)
            self._markerAndText(colorCol)

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
        #pdb.set_trace()
        super().GetChartTrace()
        #table = Table(self.DataFrame).GetChartTrace()
        return [self.goType(x = self.DataFrame[self.Xcol].values , y = self.DataFrame[self.Ycol].values ,  **self.config)]


class GroupedBar(Chart):

    def GetChartTrace(self):
        super().GetChartTrace()
        groupBy = self.config["groupby"]
        self.DataFrame.groupby(groupBy)
        return [self.goType(x = self.DataFrame[self.Xcol].values , y = self.DataFrame[self.Ycol].values ,  **self.config)]

class Scatter(Chart):

    def __init__(self, goType, dataFrame , xCol , yCol , config):
        self.Zcol = 'sizeBy'

        super(Scatter, self).__init__(goType, dataFrame,xCol , yCol , config)


    def GetChartTrace(self):
        super().GetChartTrace()
        self.config['marker']['size'] = self.DataFrame[self.Zcol].tolist()
        #print(self.config['marker']['size'])
        return [self.goType(x=self.DataFrame[self.Xcol] , y=self.DataFrame[self.Ycol] ,**self.config)]

class TrendAnimation(Chart):
    def __init__(self, dataFrame ,yearCols,yCol,config):
        config['mode'] = config.get("mode" , "markers+text")
        #pdb.set_trace()
        self.config = config
        self.yearCols = [col for col in yearCols.split(",")]
        self.yCol = yCol
        self.duration = self.GetDuration()
        super(TrendAnimation,self).__init__("scatter" , dataFrame , yearCols[0] ,yCol , self.config)

    def GetDuration(self):
        return self.config.get('locked' , dict()).get('animation' , dict()).get("duration" , 1000)

    def GetSliderStep(self,col):

        return  {   'args': [
                            [col],
                            {'frame': {'duration': self.duration, 'redraw': False},
                             'mode': 'immediate',
                           'transition': {'duration': 300}}
                         ],
                    'label': col,
                    'method': 'animate'
                }

    def GetSlidersDict(self):
        return  {
            'active': 0,
            'yanchor': 'top',
            'xanchor': 'left',
            'currentvalue': {
                'font': {'size': 20},
                'prefix': 'Year:',
                'visible': True,
                'xanchor': 'right'
            },
            'transition': {'duration': 300, 'easing': 'elastic'},
            'pad': {'b': 10, 't': 50},
            'len': 0.9,
            'x': 0.1,
            'y': 0,
            'steps': []
        }

    def Frame(self,col,min,max):
        config = copy.deepcopy(self.config)
        config['locked']['sizeCol'] = col
        config['locked']['textCol'] = self.yCol
        #frames.append(go.Frame(name = col , data=Chart("scatter" ,self.DataFrame , col , self.yCol , self.config).GetChartTrace()))
        self.frames.append(go.Frame(name = col , data=Chart("scatter" ,self.DataFrame ,col, self.yCol  , config).GetChartTrace()))
        min = min if self.DataFrame[col].min() > min else self.DataFrame[col].min()
        max = max if self.DataFrame[col].max() < max else self.DataFrame[col].max()

        self.sliders_dict['steps'].append(self.GetSliderStep(col))
        return min,max

    def Figure(self ,min,max):
        self.fig['layout']['sliders'] = [self.sliders_dict]
        self.fig['frames']= self.frames
        self.fig['layout'].update({
            'yaxis': {'showgrid':False},
            'xaxis': {'autorange':False ,'range':[min , max] },
            'updatemenus': [{   'type': 'buttons',
                                'direction': 'left',
                                'pad': {'r': 10, 't': 87},
                                'showactive': False,
                                'type': 'buttons',
                                'x': 0.1,
                                'xanchor': 'right',
                                'y': 0,
                                'yanchor': 'top',
                                'buttons': [    {
                                                    'args': [None, {'frame': {'duration': self.duration, 'redraw': False},'mode':'immediate','transition': {'duration': 300, 'easing': 'quad'}}],
                                                    'label': 'Play',
                                                    'method': 'animate'
                                                }
                                           ]
                            }]
        })

    def UpdateFigure(self):
        #pdb.set_trace()
        self.yearCols = [self.GetCol(col) for col in self.yearCols]
        self.yCol = self.GetCol(self.yCol)
        self.frames = []
        min = sys.maxsize
        max = 0
        self.config['locked'] = self.config.get('locked' , dict())
        self.config['locked']['disableQuantileSort'] = True
        self.config['mode']= "markers+text"

        self.sliders_dict = self.GetSlidersDict()
        for i,col in enumerate(self.yearCols):
            min,max = self.Frame(col,min,max)
            #frames.append({'data' : [{'x' : self.DataFrame[col] ,'y':self.DataFrame[self.yCol]}] })
        self.Figure(min,max)




class TrendChart(Chart):
    def __init__(self, dataFrame ,yearCols,yCol,yVal,config):
        columns = [dataFrame.columns[int(col)] for col in yearCols.split(",")]
        yCol = dataFrame.columns[yCol]
        df = dataFrame.loc[dataFrame[yCol] == yVal][columns].T
        df[yVal] = df.iloc[:,0].values
        df['Year'] = columns
        super(TrendChart, self).__init__('scatter', df,'Year' , yVal , config)

class TimeLine(ChartBuilderBase):

    class Params(Enum):
        animated=1

    def __init__(self,dataFrame,timeCol,eventCol,config):
        #pdb.set_trace()
        self.timeCol = GetCol(dataFrame , timeCol)
        self.eventCol = GetCol(dataFrame ,eventCol)
        self.dataFrame = dataFrame
        self.traces = []
        self.config = config

        config["mode"] = "lines+markers+text"
        config["textposition"] = 'middle center'
        config["showlegend"] = False
        config['marker'] = dict(
            symbol = "square-open"
        )
        baseheight= 15
        basestep = 7
        height = baseheight
        direction = 1
        step = basestep
        size = 0

        super(TimeLine , self).__init__(self.dataFrame , {})
        endFrame = len(self.dataFrame.index)-1 if self.IsAnimated() else 15
        #print("AAAAAAAAAAAAAAAAAAAAAAAAAA", str(pd.to_datetime(self.dataFrame.iloc[0][self.timeCol].astype(int).astype(str) ,format="%Y" )) , self.dataFrame.iloc[0][self.timeCol].dtype == 'float64' )
        if self.dataFrame.iloc[0][self.timeCol].dtype == 'float64':
            start = self.dataFrame.iloc[0][self.timeCol].astype(int).astype(str)
            end =  self.dataFrame.iloc[endFrame][self.timeCol].astype(int).astype(str)
        else:
            start = self.dataFrame.iloc[0][self.timeCol].astype(str)
            end = self.dataFrame.iloc[endFrame][self.timeCol].astype(str)


        minHeight = 0
        for i,time in enumerate(self.dataFrame[self.timeCol].unique()):
            events = self.dataFrame[self.dataFrame[self.timeCol] == time][self.eventCol].values
            #print(events , len(events))
            if i % 10  == 0:
                usedHeights = {0:True}
            rows = []
            #height = baseheight + direction*baseheight/2
            height = baseheight
            step = (height)/2
            for j,event in enumerate(events):

                while height in usedHeights:
                    height -= step

                minHeight = height if height < minHeight else minHeight
                #height = (-1*height) if direction < 0 else abs(height)-step if abs(height)-step > 0 else baseheight
                rows.append([event,height,time,size])
                usedHeights[height] = True

                #height = height-step
                if height < -1*baseheight:
                #if height < 0:
                    height = baseheight
                #height = random.random()*direction*height + step*direction

            direction = (direction + 5) % 15
            rows.append(["-",0,time,0])
            nDf = pd.DataFrame(data=rows , columns=[self.eventCol ,"Height", self.timeCol,'sizeBy'])
            self.traces.append(GetScatterChart( nDf , "2" ,"1", "0" , config).GetChartTrace()[0])

        layoutConfig = dict(

            xaxis=dict(
                range=[ start , end],
                rangeslider=dict(
                    visible = True
                ),
                type='date'
            ),
            yaxis = dict(range=[ minHeight-10 , baseheight+10],autorange=False)

        )

        layoutConfig = self.HandleAnimation(layoutConfig)
        self.layoutConfig = layoutConfig
        #pdb.set_trace()

    def IsAnimated(self):
        return TimeLine.Params.animated.name in self.config['locked']

    def HandleAnimation(self,layoutConfig):
        if self.IsAnimated():
            layoutConfig['updatemenus'] = [{'type': 'buttons',
                                      'buttons': [{'label': 'Play',
                                                   'method': 'animate',
                                                   'args': [None]}]}]

        return layoutConfig

    def GetChart(self):
        #pdb.set_trace()
        if self.IsAnimated():
            self.figure = go.Figure(data=[self.traces[0]])
            #self.figure['frames'] = [{'data':[self.traces[i]]} for i,trace in enumerate(self.traces)]
            traces = {'x':[] , 'y':[]}
            for i,trace in enumerate(self.traces):
                traces['x'].extend(trace['x'])
                traces['y'].extend(trace['y'])

            self.figure['frames'] = [{'data':[traces]}]
            self.UpdateFigure(self.figure)
        return super().GetChart()

    def GetChartTrace(self):
        return self.traces

class SingleAxisChart(Chart):
    def __init__(self,goType, dataFrame , col ,axis, config):
        self.axis = axis
        config["layoutConfig"]["margin"] = go.Margin(
                l=150,
                r=75,
                b=10,
                t=50,
                pad=4
            )

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

class Pie(Chart):

    def __init__(self,title, values , labels,config):
        workingConfig = copy.deepcopy(config)
        maxLength = plotting["Pie"]["label_max_length"]
        layoutConfig= dict(title = title
                         , xaxis = dict(title="X-axis")
                         , yaxis = dict(title = "Y-Axis")
                         , legend=dict(x=-.1, y=1.2))
        self.Values= values
        self.Labels = ["{0}...".format(label[:maxLength]) for label in labels]
        workingConfig["layoutConfig"] = {**layoutConfig , **workingConfig.get('layoutConfig' ,dict())}
        self.config = workingConfig

        super(Pie, self).__init__("pie",pd.DataFrame(columns=self.Labels , data=[self.Values]),0,0,self.config)

    def GetChartTrace(self):
        #print(self.config)
        #super().super().GetChartTrace()
        if('locked' in self.config):
            del self.config['locked']
        return [go.Pie(values = self.Values , labels = self.Labels ,  **self.config)]

    def SetupTextAndColors(self):
        self.config['marker'] = dict(colors =  plotting["ColorSchemes"]["Pie"])

    @staticmethod
    def GetMultiplePieCharts(dataFrame ,selectedXColArr,yCol , config):
        dataFrame = dataFrame.fillna(0)
        unqValues = dataFrame[yCol].unique()
        return [ Pie(value  , dataFrame.loc[dataFrame[yCol] == value][selectedXColArr].values.tolist()[0] , selectedXColArr,config) for i , value  in enumerate(unqValues)]

class Table(ChartBuilderBase):

    def __init__(self,dataFrame , config=dict()):
        self.DataFrame = dataFrame
        self.config = config
        super(Table , self).__init__(dataFrame)

    def GetChartTrace(self):
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

class MultiPlot(ChartBuilderBase):
    def __init__(self, chartsTraceArr , layout):
        #pdb.set_trace()
        self.config = {}
        fig = tools.make_subplots(**layout)
        rows = layout["rows"]
        cols = layout["cols"]

        r,c = 1,1
        for i,trace in enumerate(chartsTraceArr):
            r += 1
            if r > rows:
                r = 1
                c += 1
                if c > cols:
                    c = 1
            fig.append_trace(trace, r,c)
        super(MultiPlot, self).__init__(None,{},fig)



def Plot(figure):
    return plot(figure, output_type='div' , config={'displayModeBar': False} , include_plotlyjs=False)

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
    #xCol = GetCol(df , xCol)
    #yCol = GetCol(df , yCol)
    #pdb.set_trace()
    if 'sizeBy' not in df.columns:
        #sizeBy = (df[df.columns[xCol]].astype(float).values - df[df.columns[yCol]].astype(float).values)
        sizeBy = 50
    else:
        sizeBy = df['sizeBy'].values

    df["sizeBy"] = sizeBy
    df["colorBy"] =  'rgb(44, 160, 101)'

    #pdb.set_trace()
    return df

def GetMappedValue(OldValue , OldMin , OldMax , NewMax , NewMin):
    return (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin

def _scatterColumnAdjust(df , col):
    if col.find("-") >=0:
        df[col] = col.split("-")[1]
        return df.columns.get_loc(col)
    else:
        return int(col)

def GetScatterChart(filename,xCol , yCol , textCol,configBase):
    pdb.set_trace()
    if type(filename) == pd.DataFrame:
        df,columns = [filename , filename.columns]
    else:
        df,columns = GetDataFrame(filename)

    xCol = _scatterColumnAdjust(df,xCol)
    yCol = _scatterColumnAdjust(df,yCol)

    df = UpdateSizeByColorByColumns(df,xCol , yCol )
    textCol = GetCol(df , textCol)
    #pdb.set_trace()
    marker =  { **{ "size":  df["sizeBy"].tolist() , "color" : df["colorBy"], "line" : dict(width = 2,)} , **configBase.get('marker' ,dict())}
    configBase['marker'] = marker
    #pdb.set_trace()
    config = { **dict(mode ='markers' , text = textCol, marker = marker) , **configBase}
    #pdb.set_trace()
    return Chart("Scattergl",df , df.columns[xCol] ,  df.columns[yCol] , config)

def GetChartHTML(filename , xAxis , yAxis ,xaxisPlot='x1', yaxisPlot = 'y1'):
    df,columns = GetDataFrame(filename)
    return Chart("Bar" , df , columns[xAxis] , columns[yAxis]  , dict(xaxis = xaxisPlot , yaxis = yaxisPlot)).GetChartHTML()

def GetChartTrace(filename , xAxis , yAxis ,xaxisPlot='x1', yaxisPlot = 'y1'):
    df,columns = GetDataFrame(filename)
    return Chart("Bar" , df , columns[xAxis] , columns[yAxis]   , dict(xaxis = xaxisPlot , yaxis = yaxisPlot)).GetChartTrace()[0]

def SeparateChartArgs(request):
    #args = {'locked' : dict()}
    #if 'locked' in request.args.to_dict():

    args = ParseJson({**request.query_params , **request.args.to_dict()})
    ndic = { **request.form.to_dict() ,**args , **request.chart_params }
    del args['locked']
    return {**ndic , **args}

def GetConfig(request):
    #pdb.set_trace()
    request.query_params = request.query_params if hasattr(request, 'query_params') else  dict()
    request.chart_params = request.chart_params if hasattr(request, 'chart_params') else  dict()
    config = SeparateChartArgs(request)
    GetFiltersIntoConfig(config)
    #SortBy(config)
    #StatOps(config)
    return config


def ParseJson(config):
    #print(config)
    dic = {'locked':{}}
    #pdb.set_trace()
    for key in config:
        try:
            #print(config[key])
            val = config[key].replace("'" , '"')
            jsObj = json.loads(val)
            dic[key] = jsObj
        except Exception:
            dic[key] = config[key]

    #print(dic)
    return dic

def GetFiltersIntoConfig(config):
    filterArr = config['locked']['filters'] if 'filters' in config['locked'] else []
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

    #pdb.set_trace()
    return filters

def SortBy(config):
    if 'sortby' in config['locked']:
        config["locked"]["sortby"] = request.args.getlist('sortby')
        #del config["sortby"]

def GetCol(df, dfColIndex):
    try:
        col = df.columns[int(dfColIndex)]
    except:
        col = dfColIndex
    return col

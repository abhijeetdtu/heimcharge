import os
import operator
import re
import pdb
import json
import random
import math

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
import copy

from config import plotting

from BusinessLogic.ExceptionHandling import *
from BusinessLogic.FileOps import *
from BusinessLogic.IndiaMap import IndiaMapModel
from BusinessLogic.Entities import DataFilter

class ChartBuilderBase:

    def __init__(self ,dataFrame, layoutConfig = {} , fig = None):
        #pdb.set_trace()
        self.DataFrame = dataFrame
        self.layoutConfig = copy.deepcopy(layoutConfig)
        self.fig = fig

        if 'locked' in self.config and 'filters' in self.config['locked']:
            x = [self.AddFilterTransform(filter.dfColIndex , filter.op , filter.value) for filter in self.config['locked']['filters']]
        if 'locked' in self.config and 'sortby' in self.config['locked']:
            col,dataType = self.config['locked']['sortby']
            self.SortBy(col,dataType)

        self.ClenseConfig()

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
        rowIndices = []
        if type(dfColIndex) == str:
            col = dfColIndex
        else:
            col = self.DataFrame.columns[dfColIndex]

        df =self.DataFrame

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

        if "margin" not in layoutConfig:
            margin=go.Margin(
                l=100,
                r=0,
                b=50,
                t=50,
                pad=4
            )
            layoutConfig["margin"] = margin
        layoutConfig["autosize"] = True
        layoutConfig["barmode"]='group'
        layoutConfig["hovermode"]='closest'
        layoutConfig["paper_bgcolor"]='rgba(0,0,0,0)'

        if self.fig != None:
            self.fig['layout'].update({**layoutConfig})
            #print(self.fig['layout'])
        else:
            layout = go.Layout(**layoutConfig )
            figure = go.Figure(data = traceArr , layout = layout)
            self.fig = figure

        return self.fig

    def ClenseConfig(self):
        if 'returnPartial' in self.config:
            del self.config['returnPartial']

    def GetChart(self):
        data = self.GetChartTrace()
        return self.PrepareFigure(self.layoutConfig, data)

    def GetChartHTML(self):
        return Markup(self.Plot(self.GetChart()))

    def Plot(self,figure):
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
        layoutConfig = self.SeparateLayoutConfig(self.config, xCol , yCol )

        super(Chart, self).__init__(dataFrame,layoutConfig)

        self.Xcol = self.GetCol(xCol)
        self.Ycol = self.GetCol(yCol)

        self.goType = getattr(go , self.GetGoType(goType))

        self.SetupMarkerColors()

    def SetupMarkerColors(self):
        try:

            quantiles = self.DataFrame[self.Xcol].quantile([0.25 , 0.5 , 0.75 , 1]).values

            colorCol = 'MarkerColor' + self.Xcol
            #print(plotting)
            selectedScheme = plotting["SelectedScheme"]
            self.DataFrame[colorCol] = plotting["ColorSchemes"][selectedScheme][0]
            self.DataFrame.loc[self.DataFrame[self.Xcol] > quantiles[0], colorCol] = plotting["ColorSchemes"][selectedScheme][1]
            self.DataFrame.loc[self.DataFrame[self.Xcol] > quantiles[1], colorCol] = plotting["ColorSchemes"][selectedScheme][2]
            self.DataFrame.loc[self.DataFrame[self.Xcol] > quantiles[2] , colorCol] = plotting["ColorSchemes"][selectedScheme][3]
            self.DataFrame = self.DataFrame.sort_values(by=self.Xcol)

            if 'text' in self.config:
                self.config['text'] = self.DataFrame[self.config['text']]

            if 'marker' not in self.config:
                self.config['marker'] = dict(color = self.DataFrame[colorCol])
            #else:

                #if 'size' in self.config['marker'] :
                #    sizeBy =  self.DataFrame[self.config['marker']['size']]
                #    normalized_size = 10*(((sizeBy-sizeBy.mean())/sizeBy.std()) + 3)
                #    self.config['marker']['size'] = normalized_size
                #self.config['marker']['color'] = self.DataFrame[colorCol]

        except Exception as e:
            try:
                self.config['marker'] = dict(color =  plotting["ColorSchemes"]["Blueiss"][0])
            except:
                pass
            HandleException(e)
            pass

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

        super().GetChartTrace()
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

class TrendChart(Chart):
    def __init__(self, dataFrame ,yearCols,yCol,yVal,config):
        columns = [dataFrame.columns[int(col)] for col in yearCols.split(",")]
        yCol = dataFrame.columns[yCol]
        df = dataFrame.loc[dataFrame[yCol] == yVal][columns].T
        df[yVal] = df.iloc[:,0].values
        df['Year'] = columns
        super(TrendChart, self).__init__('scatter', df,'Year' , yVal , config)

class TimeLine(ChartBuilderBase):

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

        #print("AAAAAAAAAAAAAAAAAAAAAAAAAA", str(pd.to_datetime(self.dataFrame.iloc[0][self.timeCol].astype(int).astype(str) ,format="%Y" )) , self.dataFrame.iloc[0][self.timeCol].dtype == 'float64' )
        if self.dataFrame.iloc[0][self.timeCol].dtype == 'float64':
            start = self.dataFrame.iloc[0][self.timeCol].astype(int).astype(str)
            end =  self.dataFrame.iloc[15][self.timeCol].astype(int).astype(str)
        else:
            start = self.dataFrame.iloc[0][self.timeCol].astype(str)
            end = self.dataFrame.iloc[15][self.timeCol].astype(str)
        layoutConfig = dict(

            xaxis=dict(
                range=[ start , end],
                rangeslider=dict(
                    visible = True
                ),
                type='date'
            )
        )


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
                #height = (-1*height) if direction < 0 else abs(height)-step if abs(height)-step > 0 else baseheight
                rows.append([event,height,time,size])
                usedHeights[height] = True

                #height = height-step
                if height < -1*baseheight:
                    height = baseheight
                #height = random.random()*direction*height + step*direction

            direction = (direction + 5) % 15
            rows.append(["-",0,time,0])
            nDf = pd.DataFrame(data=rows , columns=["Event" ,"Height", "Time",'sizeBy'])
            self.traces.append(GetScatterChart( nDf , "2" ,"1", "0" , config).GetChartTrace()[0])

        #pdb.set_trace()
        super(TimeLine , self).__init__(self.dataFrame , layoutConfig)

    def GetChartTrace(self):
        return  self.traces

class SingleAxisChart(Chart):
    def __init__(self,goType, dataFrame , col ,axis, config):
        self.axis = axis
        config["layoutConfig"]["margin"] = margin=go.Margin(
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
        workingConfig["layoutConfig"] = {**layoutConfig , **( workingConfig["layoutConfig"] if 'layoutConfig' in workingConfig else dict())}
        self.config = workingConfig

        super(Pie, self).__init__("pie",pd.DataFrame(columns=self.Labels , data=[self.Values]),0,0,self.config)

    def GetChartTrace(self):
        print(self.config)
        super().GetChartTrace()
        return [go.Pie(values = self.Values , labels = self.Labels ,  **self.config)]

    def SetupMarkerColors(self):
        self.config['marker'] = dict(colors =  plotting["ColorSchemes"]["Pie"])

    @staticmethod
    def GetMultiplePieCharts(dataFrame ,selectedXColArr,yCol , config):
        dataFrame = dataFrame.fillna(0)
        unqValues = dataFrame[yCol].unique()
        return [ Pie(value  , dataFrame.loc[dataFrame[yCol] == value][selectedXColArr].values.tolist()[0] , selectedXColArr,config) for i , value  in enumerate(unqValues)]

class Table():

    def __init__(self,dataFrame):
        self.DataFrame = dataFrame

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

    def GetChart(self):
        data = [self.GetChartTrace()]

        figure = go.Figure(data = data)

        return figure

    def GetChartHTML(self):
        return Markup(self.Plot(self.GetChart()))

    def Plot(self,figure):
        return plot(figure, output_type='div' , config={'displayModeBar': False} , include_plotlyjs=False)

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
        sizeBy = (df[df.columns[xCol]].astype(float).values - df[df.columns[yCol]].astype(float).values)
    else:
        sizeBy = df['sizeBy'].values

    colorBy = [ 'rgb(255, 144, 14)' if x < 0 else 'rgb(44, 160, 101)' for x in sizeBy]

    if 'sizeBy' not in df.columns:
        sizeBy = (sizeBy-sizeBy.mean())/sizeBy.std()
        sizeBy = list(map(lambda x: abs(x)*20, sizeBy))
        #print(sizeBy)
        df["sizeBy"] = sizeBy

    df["colorBy"] = colorBy

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

def GetConfig(request):
    request.manual_params = request.manual_params if hasattr(request, 'manual_params') else  dict()
    request.chart_params = request.chart_params if hasattr(request, 'chart_params') else  dict()
    config =  { **request.form.to_dict() , **request.args.to_dict() ,"locked":{**request.manual_params} , **request.chart_params }
    config = ParseJson(config)
    GetFiltersIntoConfig(config)
    SortBy(config)

    return config

def ParseJson(config):
    print(config)
    for key in config:
        try:
            print(config[key])
            jsObj = json.loads(config[key])
            config[key] = jsObj
        except Exception as e:
            print(e)
            pass
    return config

def GetFiltersIntoConfig(config):
    filterArr = config['locked']['filter'] if 'filter' in config['locked'] else []
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

import os

import folium

from flask import Markup

import plotly.plotly as py
from plotly import tools
from plotly.offline import plot

import plotly.graph_objs as go

from branca.utilities import split_six
from config import plotting

from BusinessLogic.FileOps import *
from BusinessLogic.IndiaMap import IndiaMapModel


class ChartBuilderBase:

    def __init__(self , layoutConfig = None):
        self.layoutConfig = layoutConfig

    #to be overriden by child
    def GetChartTrace():
        return []

    def PrepareFigure(self,layoutConfig , traceArr):        
        layout = go.Layout( **layoutConfig)
        figure = go.Figure(data = traceArr , layout = layout)

        return figure

    def GetChart(self):
        data = self.GetChartTrace()
        return self.PrepareFigure(self.layoutConfig, data)

    def GetChartHTML(self):
        return Markup(self.Plot(self.GetChart()))

    def Plot(self,figure):
        return plot(figure, output_type='div' , config={'displayModeBar': False} , include_plotlyjs=False)

class Chart(ChartBuilderBase):

    def __init__(self, goType, dataFrame , xCol , yCol , config):
        layoutConfig= dict(xaxis = dict(title=xCol) , yaxis = dict(title = yCol))
        self.DataFrame = dataFrame
        self.Xcol =xCol
        self.Ycol = yCol
        self.goType = goType
        self.config = config

        super(Chart, self).__init__(layoutConfig)

    def GetChartTrace(self):
        return [self.goType(x = self.DataFrame[self.Xcol] , y = self.DataFrame[self.Ycol] ,  **self.config)]

class StackedBar(ChartBuilderBase):

    def __init__(self, dataFrame , selectedXColArr , yCol , config):
        layoutConfig= dict(xaxis = dict(title="X-axis") , yaxis = dict(title = yCol),barmode='stack')
        self.DataFrame = dataFrame
        self.SelectedXColArr = selectedXColArr
        self.Ycol = yCol
        self.config = config

        super(StackedBar, self).__init__(layoutConfig)

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

        super(Pie, self).__init__(layoutConfig)

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


def IndiaMap(df ,colorBy, columns):
    state_geo =  os.path.abspath(os.path.join('Data', 'indiageojson.json'))
    m = folium.Map(location=[plotting["India"]["Center"]["Lat"], plotting["India"]["Center"]["Long"]], zoom_start=plotting["DefaultZoom"])
    threshold_scale = split_six(df[colorBy])

    m.choropleth(
            geo_data=state_geo,
            data = df,
            columns=columns,
            name='choropleth',
            key_on='feature.id',
            fill_color='YlGn',
            fill_opacity=0.7,
            line_opacity=0.2,
            threshold_scale=threshold_scale,
            legend_name=colorBy
    )

    folium.LayerControl().add_to(m)

    return IndiaMapModel(colorBy , "" , m)


def GetMappedValue(OldValue , OldMin , OldMax , NewMax , NewMin):
    return (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin

def GetScatterChart(filename,xCol , yCol , textCol):
    df,columns = GetDataFrame(filename)

    sizeBy = (df[df.columns[xCol]].astype(float).values - df[df.columns[yCol]].astype(float).values)
        
    colorBy = [ 'rgb(255, 144, 14)' if x < 0 else 'rgb(44, 160, 101)' for x in sizeBy]

    sizeBy = (sizeBy-sizeBy.mean())/sizeBy.std()
    sizeBy = list(map(lambda x: abs(x)*50, sizeBy))

    config = dict(mode ='markers+text' , text = df[df.columns[textCol]], marker = dict(size=  sizeBy , color = colorBy, line = dict(width = 2,)))
    return Chart(go.Scatter,df , df.columns[xCol] ,  df.columns[yCol] , config)

def GetChartHTML(filename , xAxis , yAxis ,xaxisPlot='x1', yaxisPlot = 'y1'):
    df,columns = GetDataFrame(filename)
    return Chart(go.Bar , df , columns[xAxis] , columns[yAxis]  , dict(xaxis = xaxisPlot , yaxis = yaxisPlot)).GetChartHTML()

def GetChartTrace(filename , xAxis , yAxis ,xaxisPlot='x1', yaxisPlot = 'y1'):
    df,columns = GetDataFrame(filename)
    return Chart(go.Bar , df , columns[xAxis] , columns[yAxis]   , dict(xaxis = xaxisPlot , yaxis = yaxisPlot)).GetChartTrace()[0]
    

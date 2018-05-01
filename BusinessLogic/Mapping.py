import os

import folium
import plotly.plotly as py
from plotly import tools
from plotly.offline import plot

import plotly.graph_objs as go

from branca.utilities import split_six
from config import plotting

from BusinessLogic.FileOps import *
from BusinessLogic.IndiaMap import IndiaMapModel

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

def SharedAxisLayout(chartArr , sharedX , sharedY,subplotTitles):
    if sharedX == True:
        return SharedXAxisLayout(chartArr,subplotTitles)
    else:
        return SharedYAxisLayout(chartArr,subplotTitles)

def SharedAxisBarCharts(chartArr , subplotTitles , chartTitle , sharedX , sharedY):
    fig = SharedAxisLayout(chartArr , sharedX , sharedY,subplotTitles)
    fig['layout'].update(showlegend=False, title=chartTitle)
    return Plot(fig)


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

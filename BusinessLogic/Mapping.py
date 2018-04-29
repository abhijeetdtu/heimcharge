import os
import json
import pandas as pd

import folium
import plotly.plotly as py
from plotly.offline import plot

import plotly.graph_objs as go

from branca.utilities import split_six
from config import plotting


def GetDataFrameFromJson(file , transform = None):
     jsonData = json.load(open(file))
     columns = [ f['label'] for f in jsonData['fields']]

     data = jsonData['data']
     df = pd.DataFrame(data = data , columns = columns)

     if transform != None:
        df = transform(df)

     return df

def PopulationTransform(df):   
     df["Population 2011"] = df["Population 2011"].astype(float)
     return df

def BarChart(df , xCol , yCol , orientation = 'h'):
    data = [
        go.Bar(
            x=df[xCol], # assign x as the dataframe column 'x'
            y=df[yCol],
            orientation = orientation
        )
    ]

    return plot(data, output_type='div' , config={'displayModeBar': False})

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
            legend_name='Unemployment Rate (%)'
    )

    folium.LayerControl().add_to(m)
    return m

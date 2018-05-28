from BusinessLogic.GeoOps import *
from BusinessLogic.IndiaMap import IndiaMapModel
from config import plotting

import os
import json

import folium
from folium.plugins import MarkerCluster
from folium.features import DivIcon
import branca.element
import branca.colormap as cm
from branca.utilities import split_six
import pandas as pd

def GetText(location , text):
    return folium.map.Marker(
    location,
    icon=DivIcon(
        icon_size=(150,36),
        icon_anchor=(0,0),
        html='<div class="folium-text">{0}</div>'.format(text),
        )
    )


def GetIconCreateFunction():
    icon_create_function = """\
        function(cluster) {
            return L.divIcon({
            html: '<b>' + cluster.getChildCount() + '</b>',
            className: 'marker-cluster marker-cluster-large',
            iconSize: new L.Point(20, 20)
            });
        }"""

    return icon_create_function

def GetPopupTemplate(title , field , value):
    html = """{0}<br/>{1}<br/>{2}"""
    return html.format(title , field ,value)

def GetLocationValue(df , locationCol ,location , valueCol):
    arr = df[df[locationCol] == location][valueCol].values
    value = 0
    if len(arr) > 0:
        value = arr[0]
    return value

def CreatePopupCluster(markerArr):
    
    marker_cluster = MarkerCluster(
        name='1000 clustered icons',
        overlay=True,
        control=True,
        icon_create_function=None
    )

    [marker_cluster.add_child(marker) for marker in markerArr]

    return marker_cluster

def GetSizeAndColor(type ,value ,mean, max , min):
    max_min = (max-min)
    if(type == 'simple'):
        size = 15 + 30*value
        color = 'red'
    if(type == 'deviationFromMean'):
        size = 15 +  (30*abs(value-mean)/(max_min+1))
        if(value-mean > 0):
            color = 'red'
        else:
            color = 'green'
    
    return [size , color]

def CreateIndividualPopups(df , locationCol , colorBy , drawingType):
    markers = []
    
    max = df[colorBy].max()
    min = df[colorBy].min()
    mean = df[colorBy].mean()

    for location in df[locationCol].unique():
        value = GetLocationValue(df , locationCol , location , colorBy)
        latLong = GetLocationLatLong(location)
        popUp = GetPopupTemplate(location ,colorBy , value)
        size,color = GetSizeAndColor(drawingType , value , mean , max,min)
        markers.append(folium.CircleMarker(fill=True,fill_color=color, radius=size, location= latLong, popup=popUp))

    return markers

def CreatePopupCirlcesForLocations(df , locationCol , colorBy , drawingType):

    unqLocations = df[locationCol].unique()
    markers = CreateIndividualPopups(df ,locationCol , colorBy , drawingType)

    # if(len(unqLocations) > 50):
    #     markers = [CreatePopupCluster(markers)]

    return markers

def IndiaMap(df ,colorBy, columns):
    state_geo =  os.path.abspath(os.path.join('Data', 'indiageojson.json'))
    m = folium.Map(location=[plotting["India"]["Center"]["Lat"], plotting["India"]["Center"]["Long"]]
                    , zoom_start=plotting["DefaultZoom"]
                    , tiles='cartodbpositron')
    
    threshold_scale = split_six(df[colorBy])
    m.choropleth(
            geo_data=state_geo,
            data = df,
            columns=columns,
            name='choropleth',
            key_on='feature.id',
            fill_color='PuBuGn',
            fill_opacity=0.7,
            line_opacity=0.2,
            threshold_scale=threshold_scale,
            legend_name=colorBy
            
    )


    markers = CreatePopupCirlcesForLocations(df , columns[0] , colorBy , 'deviationFromMean')
    [marker.add_to(m) for marker in markers]

    #GetText([12,86] , ).add_to(m)
    folium.LayerControl().add_to(m)

    return IndiaMapModel(colorBy ,  'Sized By Deviation From Mean : {0}<br/> Green < Mean <br/> Red > Mean'.format(df[colorBy].mean()) , m)


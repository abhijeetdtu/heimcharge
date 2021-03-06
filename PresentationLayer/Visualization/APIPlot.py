from flask import Blueprint,render_template , Markup ,request , jsonify,url_for
from jinja2 import TemplateNotFound
import json

from API.ApiOps import *
from API.RestBase import Rest as RT
from BusinessLogic.Mapping import *
from BusinessLogic.GeoProcessing import *

import PresentationLayer.Visualization.Helpers as Helpers

import PresentationLayer.Visualization._chartHelpers as Helpers

APIPlot = Blueprint('APIPlot', __name__,template_folder='templates')

api_base_config = {}
api_base_config["layoutConfig"] = dict(xaxis = dict(side = 'top'))
api_base_config["orientation"]='h'



def GetParams(request , xy ,isHorizontalFromGet, df):
    method = request.method
    isHorizontal = 'v'
    if method == "POST":
        print(request.form)
        x = request.form["XAxis"]
        y = request.form["YAxis"]

        if "IsHorizontal" in request.form:
            isHorizontal = 'h'

    else:
        if isHorizontalFromGet:
            isHorizontal = 'h'

        if xy:
            x,y = xy.split(",")
            try:
                print(df.columns)
                x = df.columns[int(x)]
                y = df.columns[int(y)]

            except:
                pass
        else:
            x,y = FindColumns(df)
    return x,y,isHorizontal

@APIPlot.route("/landing" , methods=["GET"])
def landing():
    links = [(link , url_for("APIPlot.plot" , resourceName= link , chartType= "bar" , returnPartial=True))  for link in  RT.GetAllAvailableResources()]
    return  Helpers.SetupParamsAndReturnTemplate("APIPlot/Landing" , request , dict(links = links))


def GetChart(chartType,df ,x , y , config):
    if chartType == "map":
        return IndiaMap(df ,y, [x,y])
    else:
        return Chart(chartType,df ,x , y , config)

@APIPlot.route("/<string:resourceName>/<string:chartType>" , methods=["GET" , "POST"])
@APIPlot.route("/<string:resourceName>/<string:chartType>/<string:xy>" , methods=["GET" , "POST"])
@APIPlot.route("/<string:resourceName>/<string:chartType>/<string:xy>/<string:isHorizontal>", methods=["GET" , "POST"])
@APIPlot.route("/<string:resourceName>/<string:chartType>/<string:xy>/<string:isHorizontal>/<string:filters>", methods=["GET" , "POST"])
def plot(resourceName ,chartType,xy=None,isHorizontal='False', filters=None):
    isHorizontal = bool(isHorizontal)
    if filters:
        filters = json.loads(filters)

    #config = {"mode":"lines"}
    config = {**api_base_config}
    df = RT.Get(resourceName, filters)
    exampleDic = json.loads(df.head(1).to_json(orient='records'))[0]
    js = json.dumps(json.loads(df.head(1).to_json(orient='records')) , indent=4 , sort_keys=True)

    baseUrl = url_for("APIPlot.plot" , resourceName="" , chartType="").strip("/")

    x,y,isHorizontal = GetParams(request , xy,isHorizontal,df)
    config['orientation'] = isHorizontal
    #barChart = Markup(BarChart(df , x , y  , 'h'))
    barChart = GetChart(chartType,df ,x , y , config).GetChartHTML()
    return  Helpers.SetupParamsAndReturnTemplate("ApiPlot",request , {"barChart":barChart , "json":js ,"resourceName":resourceName,"chartType" :chartType, "exampleDic":exampleDic , "url":baseUrl})



"""
@APIPlot.route("/airquality/bar")
@APIPlot.route('/airquality/bar/<string:city>')
@APIPlot.route('/airquality/bar/<string:city>/<string:pollutant_id>')
def aqbar(city="Delhi", pollutant_id="NO2"):
    df = RT.Get("" , dict(city=city , pollutant_id=pollutant_id))
    print(df)
    barCharts = [Markup(BarChart(df , "pollutant_avg" , "station"  , 'h'))]
    return SetupParamsAndReturnFilePlot(request , barCharts)


@APIPlot.route("/airquality/map")
@APIPlot.route('/airquality/map/<string:city>')
@APIPlot.route('/airquality/map/<string:city>/<string:pollutant_id>')
def aqmap(city="Delhi", pollutant_id="NO2"):
    df = RT.Get("AirQuality",{})
    exampleDic = json.loads(df.head(1).to_json(orient='records'))[0]

    columns = ['city', 'pollutant_avg']
    colorBy = 'pollutant_avg'
    m = IndiaMap(df ,colorBy, columns)
    return  Helpers.SetupParamsAndReturnTemplate("ApiPlot",request , {"barChart":m.Html , "json":{} ,"resourceName":"","chartType" :"map", "exampleDic":exampleDic , "url":""})
"""

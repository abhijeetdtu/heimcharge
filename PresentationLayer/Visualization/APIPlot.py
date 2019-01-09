from flask import Blueprint,render_template , Markup ,request , jsonify
from jinja2 import TemplateNotFound
import json

from API.RestBase import Rest as RT
from BusinessLogic.Mapping import *
from BusinessLogic.GeoProcessing import *

import PresentationLayer.Visualization.Helpers as Helpers

from PresentationLayer.Visualization.ChartPlot import SetupParamsAndReturnTemplate

APIPlot = Blueprint('APIPlot', __name__,template_folder='templates')

api_base_config = {}
api_base_config["layoutConfig"] = dict(xaxis = dict(side = 'top'))
api_base_config["orientation"]='h'

def GetParams(request , xy , df):
    method = request.method
    isHorizontal = 'v'
    if method == "POST":
        print(request.form)
        x = request.form["XAxis"]
        y = request.form["YAxis"]

        if "IsHorizontal" in request.form:
            isHorizontal = 'h'

    else:
        if xy:
            x,y = xy.split(",")
        else:
            x = df.columns[0]
            y = df.columns[1]
    return x,y,isHorizontal

@APIPlot.route("/<string:resourceName>/<string:chartType>" , methods=["GET" , "POST"])
@APIPlot.route("/<string:resourceName>/<string:chartType>/<string:xy>" , methods=["GET" , "POST"])
@APIPlot.route("/<string:resourceName>/<string:chartType>/<string:xy>/<string:filters>/", methods=["GET" , "POST"])
def plot(resourceName ,chartType,xy=None, filters=None):
    if filters:
        filters = json.loads(filters)

    #config = {"mode":"lines"}
    config = {**api_base_config}

    df = RT.Get(resourceName, filters)

    url = Helpers.GetPathPrefix(request , f"/{resourceName}/{chartType}") + f"/{resourceName}/{chartType}"

    exampleDic = json.loads(df.head(1).to_json(orient='records'))[0]
    js = json.dumps(json.loads(df.head(1).to_json(orient='records')) , indent=4 , sort_keys=True)

    x,y,isHorizontal = GetParams(request , xy,df)
    config['orientation'] = isHorizontal
    #barChart = Markup(BarChart(df , x , y  , 'h'))
    barChart = Chart(chartType,df ,x , y , config).GetChartHTML()
    return SetupParamsAndReturnTemplate("ApiPlot",request , {"barChart":barChart , "json":js , "exampleDic":exampleDic})



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
    df = AQ.GetDataFrame(city , pollutant_id)
    columns = ['city', 'pollutant_avg']
    colorBy = 'pollutant_avg'
    m = IndiaMap(df ,colorBy, columns)

    return SetupParamsAndReturnFilePlot(request , [m.Html])
"""
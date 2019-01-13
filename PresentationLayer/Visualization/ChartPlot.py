from flask import Blueprint,render_template , Markup ,request
from jinja2 import TemplateNotFound

from BusinessLogic.Entities import *
from BusinessLogic.Mapping import *
from BusinessLogic.FileOps import *
from BusinessLogic.ExceptionHandling import *
from API.RestBase import Rest as RT
import os,re
from config import files
import sys , traceback

ChartPlot = Blueprint('ChartPlot', __name__,template_folder='templates')

@ChartPlot.route("/")
def index():
    try:
        df,columns = GetDataFrame("stateWisePopulation")
        config = {}
        chart = Chart("Scatter",df , df.columns[1] ,  df.columns[2] , config)
        return render_template('FilePlot.html' , bar_charts = [chart.GetChartHTML()])

    except Exception as e:
        return HandleException(e)

def SetupParamsAndReturnTemplate(template , request , params):
    returnPartial = (request.args.get('returnPartial') or None) == 'True'
    params["returnPartial"] = returnPartial
    return render_template(f'{template}.html' ,**params)

def SetupParamsAndReturnFilePlot(template , request  , bar_charts):
    returnPartial = (request.args.get('returnPartial') or None) == 'True'
    return render_template(f'{template}.html' ,returnPartial = returnPartial, bar_charts = bar_charts)


@ChartPlot.route("/api/<string:plotName>/<string:resourceName>/<int:xCol>/<int:yCol>/<string:isHorizontal>" , methods = ['GET' , 'POST'])
def apiplot(plotName,resourceName,xCol , yCol,isHorizontal):
    try:
        print("hit the endpoint")
        df = RT.Get(resourceName, {})
        config = request.form or {}
        config['orientation'] = isHorizontal

        #print(config)
        chart = Chart(plotName,df , df.columns[xCol] ,  df.columns[yCol] , config)
        return SetupParamsAndReturnFilePlot("FilePlot",request ,[chart.GetChartHTML()])

    except Exception as e:
        return HandleException(e)

@ChartPlot.route("/chart/<string:plotName>/<string:filename>/<int:xCol>/<int:yCol>" , methods = ['GET' , 'POST'])
def plot(plotName,filename,xCol , yCol):
    try:
        df,columns = GetDataFrame(filename)
        config = request.form

        chart = Chart(plotName,df , df.columns[xCol] ,  df.columns[yCol] , config)
        return SetupParamsAndReturnFilePlot("FilePlot",request ,[chart.GetChartHTML()])

    except Exception as e:
        return HandleException(e)

@ChartPlot.route("/table/<string:filename>/")
def GetTable(filename):
        df,columns = GetDataFrame(filename)
        config = {}
        chart = Table(df)
        return SetupParamsAndReturnFilePlot("FilePlot",request ,[chart.GetChartHTML()])


@ChartPlot.route("/scatter/<string:filename>/<int:xCol>/<int:yCol>/<int:textCol>")
def scatter( filename,xCol , yCol , textCol):
    try:
        config = GetConfig(request)
        chart = GetScatterChart(filename,xCol , yCol , textCol , config)
        return SetupParamsAndReturnFilePlot("FilePlot",request ,[chart.GetChartHTML()])

    except Exception as e:
        return HandleException(e)

@ChartPlot.route("/scattersize/<string:resourceName>/<int:xCol>/<int:yCol>/<int:sizeCol>/<int:textCol>")
def scatterSize( resourceName,xCol , yCol ,sizeCol,textCol):
    try:
        configBase = GetConfig(request)
        df = RT.Get(resourceName, {})


        config = dict(mode ='markers' , text = df.columns[textCol], marker = dict(size=  df.columns[sizeCol] , line = dict(width = 2,)))
        print(df.columns)
        for key in configBase:
            config[key] = configBase[key]

        chart = Chart("Scatter",df , df.columns[xCol] ,  df.columns[yCol] , config)
        return SetupParamsAndReturnFilePlot("FilePlot",request ,[chart.GetChartHTML()])

    except Exception as e:
        return HandleException(e)

@ChartPlot.route("/stacked/<string:filename>/<int:yCol>/<string:commaSeparatedColumns>")
def stacked(filename,yCol,commaSeparatedColumns):
    try:
        df,columns = GetDataFrame(filename)
        selectedColumns = list(map( lambda x: df.columns[int(x)] , commaSeparatedColumns.split(',')))
        yCol = df.columns[yCol]
        config = dict( orientation = 'h')

        print(selectedColumns)
        chart = StackedBar(df,selectedColumns ,yCol,config)

        return SetupParamsAndReturnFilePlot("FilePlot",request ,[chart.GetChartHTML()])

    except Exception as e:
        return HandleException(e)


@ChartPlot.route("/pie/<string:filename>/<int:yCol>/<string:commaSeparatedColumns>")
def pie(filename,yCol,commaSeparatedColumns):
    try:
        df,columns = GetDataFrame(filename)
        selectedColumns = list(map( lambda x: df.columns[int(x)] , commaSeparatedColumns.split(',')))
        yCol = df.columns[yCol]
        config = dict()

        charts = Pie.GetMultiplePieChartsHTML(df , selectedColumns , yCol , config)
        return SetupParamsAndReturnFilePlot("FilePlot",request ,charts)

    except Exception as e:
        return HandleException(e)



@ChartPlot.route('/crossFile/<string:fileA>/<int:xAxisFileA>/<int:yAxisFileA>/<string:fileB>/<int:xAxisFileB>/<int:yAxisFileB>/<int:sharedX>/<int:sharedY>/<string:normalize>')
def plotTogether(fileA , xAxisFileA , yAxisFileA ,fileB, xAxisFileB ,yAxisFileB, sharedX , sharedY , normalize):
    try:

        if sharedX == 1:
            sharedX = 'x1'
        else:
            sharedX = 'x2'

        if sharedY == 1:
            sharedY = True
        else:
            sharedY = False

        normalize = bool(normalize)
        charts = [GetChartTrace(fileA , xAxisFileA , yAxisFileA ,'x1' ,  'y1') , GetChartTrace(fileB , xAxisFileB , yAxisFileB ,'x2', 'y2')]
        chartTitles = ["X-axix" , "Y-axsx"]

        sharedChart = SharedAxisBarCharts(charts , chartTitles , "Together" , sharedX ,sharedY)
        return SetupParamsAndReturnFilePlot("FilePlot",(request ,[Markup(sharedChart)]))
    except TemplateNotFound:
        abort(404)

from flask import Blueprint,render_template , Markup ,request
from jinja2 import TemplateNotFound

from BusinessLogic.Mapping import *
from BusinessLogic.FileOps import *

import os
from config import files
import sys , traceback

ChartPlot = Blueprint('ChartPlot', __name__,template_folder='templates')

@ChartPlot.route("/")
def index():
    try:
        df,columns = GetDataFrame("stateWisePopulation")
        config = {}
        chart = Chart(getattr(go , "Scatter"),df , df.columns[1] ,  df.columns[2] , config)
        return render_template('FilePlot.html' , bar_charts = [chart.GetChartHTML()])

    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("*** print_tb:")
        traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
        traceback.print_exception(exc_type, exc_value, exc_traceback,limit=2, file=sys.stdout)
        return Error404()


@ChartPlot.route("/chart/<string:plotName>/<string:filename>/<int:xCol>/<int:yCol>" , methods = ['GET' , 'POST'])
def plot(plotName,filename,xCol , yCol):
    try:
        df,columns = GetDataFrame(filename)
        config = request.form

        chart = Chart(getattr(go , plotName),df , df.columns[xCol] ,  df.columns[yCol] , config)
        return render_template('FilePlot.html' , bar_charts = [chart.GetChartHTML()])

    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("*** print_tb:")
        traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
        traceback.print_exception(exc_type, exc_value, exc_traceback,limit=2, file=sys.stdout)
        return Error404()

@ChartPlot.route("/table/<string:filename>/")
def GetTable(filename):
        df,columns = GetDataFrame(filename)
        config = {}
        chart = Table(df)
        return render_template('FilePlot.html' , bar_charts = [chart.GetChartHTML()])


@ChartPlot.route("/scatter/<string:filename>/<int:xCol>/<int:yCol>/<int:textCol>")
def scatter(filename,xCol , yCol , textCol):
    try:
        df,columns = GetDataFrame(filename)

        sizeBy = (df[df.columns[xCol]].astype(float).values - df[df.columns[yCol]].astype(float).values)
        
        colorBy = [ 'rgb(255, 144, 14)' if x < 0 else 'rgb(44, 160, 101)' for x in sizeBy]

        sizeBy = (sizeBy-sizeBy.mean())/sizeBy.std()
        
        sizeBy = list(map(lambda x: abs(x)*20 , sizeBy))

        config =  dict(mode ='markers+text' , text = df[df.columns[textCol]], marker = dict(size=  sizeBy , color = colorBy, line = dict(
            width = 2,
        ) ) )
        chart = Chart(go.Scatter,df , df.columns[xCol] ,  df.columns[yCol] , config)
        return render_template('FilePlot.html' , bar_charts = [chart.GetChartHTML()])

    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("*** print_tb:")
        traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
        traceback.print_exception(exc_type, exc_value, exc_traceback,limit=2, file=sys.stdout)
        return Error404()

@ChartPlot.route("/stacked/<string:filename>/<int:yCol>/<string:commaSeparatedColumns>")
def stacked(filename,yCol,commaSeparatedColumns):
    try:
        df,columns = GetDataFrame(filename)
        selectedColumns = list(map( lambda x: df.columns[int(x)] , commaSeparatedColumns.split(',')))
        yCol = df.columns[yCol]
        config = dict( orientation = 'h')

        print(selectedColumns)
        chart = StackedBar(df,selectedColumns ,yCol,config)
        
        return render_template('FilePlot.html' , bar_charts = [chart.GetChartHTML()])

    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("*** print_tb:")
        traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
        traceback.print_exception(exc_type, exc_value, exc_traceback,limit=2, file=sys.stdout)
        return Error404()


@ChartPlot.route("/pie/<string:filename>/<int:yCol>/<string:commaSeparatedColumns>")
def pie(filename,yCol,commaSeparatedColumns):
    try:
        df,columns = GetDataFrame(filename)
        selectedColumns = list(map( lambda x: df.columns[int(x)] , commaSeparatedColumns.split(',')))
        yCol = df.columns[yCol]
        config = dict()

        charts = Pie.GetMultiplePieChartsHTML(df , selectedColumns , yCol , config)
        return render_template('FilePlot.html' , bar_charts = charts)

    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("*** print_tb:")
        traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
        traceback.print_exception(exc_type, exc_value, exc_traceback,limit=2, file=sys.stdout)
        return Error404()



@ChartPlot.route('/crossFile/<string:fileA>/<int:xAxisFileA>/<int:yAxisFileA>/<string:fileB>/<int:xAxisFileB>/<int:yAxisFileB>/<int:sharedX>/<int:sharedY>')
def plotTogether(fileA , xAxisFileA , yAxisFileA ,fileB, xAxisFileB ,yAxisFileB, sharedX , sharedY):
    try:
        
        if sharedX == 1:
            sharedX = True
        else:
            sharedX = False

        if sharedY == 1:
            sharedY = True
        else:
            sharedY = False
        
        charts = [GetChartTrace(fileA , xAxisFileA , yAxisFileA) , GetChartTrace(fileB , xAxisFileB , yAxisFileB)]
        chartTitles = ["X-axix" , "Y-axsx"]

        sharedChart = SharedAxisBarCharts(charts , chartTitles , "Together" , sharedX ,sharedY)

        return render_template('FilePlot.html' , bar_charts = [Markup(sharedChart)])

    except TemplateNotFound:
        abort(404)


def GetChartTrace(filename , xAxis , yAxis):
    df,columns = GetDataFrame(filename)
    return Chart(go.Bar , df , columns[xAxis] , columns[yAxis]  , dict()).GetChartTrace()[0]
    
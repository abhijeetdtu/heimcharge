from flask import Blueprint,render_template , Markup
from flask import request
from jinja2 import TemplateNotFound
import plotly.graph_objs as go


from BusinessLogic.Mapping import *
from BusinessLogic.FileOps import *

import copy
import os
from config import files

IndiaBasePlot = Blueprint('IndiaBasePlot', __name__,template_folder='templates')


@IndiaBasePlot.route('/')
def show():
    try:
        
        dataFile = files["StateWisePop"]
        df = GetDataFrameFromJson(dataFile , PopulationTransform)

        columns = ['India / State/ Union Territory', 'Population 2011']
        colorBy = 'Population 2011'
        m = IndiaMap(df ,colorBy, columns)

        barCharts = [Markup(BarChart(df , column , columns[0]  , 'h')) for column in list(df.columns) if column != columns[0]]

        
        return render_template('BaseMap.html' ,map = m, bar_charts = barCharts)

    except TemplateNotFound:
        abort(404)


@IndiaBasePlot.route('/plotFile/<string:filename>/<int:xAxisIndex>')
def plotFile(filename , xAxisIndex):
    try:
        df,columns = GetDataFrame(filename)
        config = dict(orientation='h' )
        barCharts = [Chart(getattr(go , "Bar"),df , column ,  columns[xAxisIndex], config) for column in columns if column != columns[xAxisIndex]]
        
        return render_template('FilePlot.html' , bar_charts = barCharts)

    except TemplateNotFound:
        abort(404)

@IndiaBasePlot.route('/plotFileWithMap/<string:filename>/<int:xAxisIndex>/<int:yAxisForMap>')
def plotFileWithMap(filename , xAxisIndex,  yAxisForMap):
    try:

        df,columns = GetDataFrame(filename)
        config = GetConfig(request)
        config["orientation"]='h'
        config["layoutConfig"] = dict(xaxis = dict(side = 'top'))
        colorBy = columns[yAxisForMap]
        df[colorBy] = df[colorBy].astype("float")
        m = IndiaMap(df ,colorBy, [columns[xAxisIndex] , columns[yAxisForMap]])
        
        barCharts = [Chart(getattr(go , "Bar"),df , column ,  columns[xAxisIndex], copy.deepcopy(config)).GetChartHTML() for column in columns if column != columns[xAxisIndex]]
        sideChart = Chart(getattr(go , "Bar"),df , colorBy ,  columns[xAxisIndex],  copy.deepcopy(config)).GetChartHTML()

        prefix = request.path[:request.path.find("/plotFileWithMap")]
        viewParams = dict(map=m , 
                          bar_charts = barCharts , 
                          side_chart = sideChart , 
                          endpoint='{0}/plotFileWithMap/{1}/{2}/#YAXIS'.format(prefix , filename,xAxisIndex)
                          )
        return render_template('BaseMap.html' , **viewParams)

    except TemplateNotFound:
        abort(404)

@IndiaBasePlot.route('/plotTogether/<string:filename>/<int:xAxisIndex>/<int:chartA>/<int:chartB>/<int:sharedX>/<int:sharedY>')
def plotTogether(filename , xAxisIndex , chartA , chartB , sharedX , sharedY):
    try:
        
        if sharedX == 1:
            sharedX = True
        else:
            sharedX = False

        if sharedY == 1:
            sharedY = True
        else:
            sharedY = False

        df,columns = GetDataFrame(filename)

        barCharts = [BarChartTrace(df , columns[chartI] , columns[xAxisIndex]  , 'h') for chartI in [chartA, chartB]]
        chartTitles = [columns[chartI] for chartI in [chartA, chartB]]

        sharedChart = SharedAxisBarCharts(barCharts , chartTitles , columns[xAxisIndex] , sharedX ,sharedY)

        return render_template('FilePlot.html' , bar_charts = [Markup(sharedChart)])

    except TemplateNotFound:
        abort(404)


@IndiaBasePlot.route('/getproperties')
def getproperties():
    try:
        
        allAvailable = []

        for filename in files:
            columns = GetColumnsFromFile(dataFile)
            allAvailable.extend(columns)

        return allAvailable

    except TemplateNotFound:
        abort(404)
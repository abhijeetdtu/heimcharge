from flask import render_template
import pdb

import BusinessLogic.Entities as Entities
import BusinessLogic.Mapping as BLM
import BusinessLogic.FileOps as FileOps

from API.RestBase import Rest as RT


def SetupParamsAndReturnTemplate(template , request , params):
    returnPartial = (request.args.get('returnPartial') or None) == 'True'
    params["returnPartial"] = returnPartial
    return render_template(f'{template}.html' ,**params)

def SetupParamsAndReturnFilePlot(template , request  , bar_charts):
    returnPartial = (request.args.get('returnPartial') or None) == 'True'
    return render_template(f'{template}.html' ,returnPartial = returnPartial, bar_charts = bar_charts)

def _chartPlot(request , plotName , filename , xCol , yCol , isHorizontal=False):
    print("hit the endpoint")
    df,columns = FileOps.GetDataFrame(filename)
    xCol = int(xCol)
    yCol = int(yCol)
    config = BLM.GetConfig(request)
    config['orientation'] = 'h' if isHorizontal == True else 'v'
    #print(config)
    return BLM.Chart(plotName,df , columns[xCol] ,  columns[yCol] , config)

def _chartTrendAnimation(request ,filename,yearCols , yCol,yVal='-'):
    df = FileOps.GetDataFrame(filename)[0]
    #pdb.set_trace()
    config = BLM.GetConfig(request)

    if yearCols.find("-") >= 0:
        fr,to = [int(t) for t in yearCols.split("-")]
        yearCols = ",".join([str(i) for i in range(fr,to)])

    return BLM.TrendAnimation(df,yearCols,yCol,config)


def _chartTrend(request , api_file,filename,yearCols , yCol,yVal='-'):
    df = RT.Get(filename, {}) if api_file == 'api' else FileOps.GetDataFrame(filename)[0]
    config = BLM.GetConfig(request)
    yCol = int(yCol)
    if yearCols.find("-") >= 0:
        fr,to = [int(t) for t in yearCols.split("-")]
        yearCols = ",".join([str(i) for i in range(fr,to)])
    if yVal != '-':
        charts = [BLM.TrendChart(df ,yearCols , yCol,yVal,config)]
    else:
        charts = [BLM.TrendChart(df ,yearCols , yCol,y,config) for y in df.iloc[:,yCol].values]

    return charts

def _chartTimeline(request,filename,timeCol,eventCol):
    df,columns = FileOps.GetDataFrame(filename)
    config = BLM.GetConfig(request)
    return BLM.TimeLine(df, timeCol, eventCol, config)

def _chartTable(request,  filename):
    df,columns = FileOps.GetDataFrame(filename)
    return  BLM.Table(df)

def _chartScatter(request,  filename,xCol , yCol , textCol):
    config = BLM.GetConfig(request)
    textCol = int(textCol)
    return BLM.GetScatterChart(filename,xCol , yCol , textCol , config)

def _chartScatterSize(request,resourceName,xCol , yCol ,sizeCol,textCol):
    configBase = BLM.GetConfig(request)
    df,columns = FileOps.GetDataFrame(resourceName)
    xCol = BLM.GetCol(df,xCol)
    yCol = BLM.GetCol(df,yCol)
    textCol = BLM.GetCol(df,textCol)
    sizeCol = BLM.GetCol(df,sizeCol)
    #pdb.set_trace()

    config = {**configBase , **dict(mode ='markers' , locked = {**configBase , **dict(textCol = textCol, sizeCol = sizeCol)}) }

    return BLM.Chart("Scatter",df , xCol , yCol , config)

def _chartStackedBar(request,filename,yCol,commaSeparatedColumns):
    df,columns = FileOps.GetDataFrame(filename)
    selectedColumns = list(map( lambda x: df.columns[int(x)] , commaSeparatedColumns.split(',')))
    yCol = df.columns[int(yCol)]
    config = dict( orientation = 'h')
    return BLM.StackedBar(df,selectedColumns ,yCol,config)

def _chartPie(request , filename,yCol,commaSeparatedColumns):
    df,columns = FileOps.GetDataFrame(filename)
    selectedColumns = list(map( lambda x: df.columns[int(x)] , commaSeparatedColumns.split(',')))
    yCol = df.columns[int(yCol)]
    config = BLM.GetConfig(request)
    return BLM.Pie.GetMultiplePieCharts(df , selectedColumns , yCol , config)


def _getChartMethod(methodName):
    possibles = globals().copy()
    possibles.update(locals())
    return possibles.get(methodName)

def _chartMultiPlot(request):
    json = request.get_json()
    chartsConfigs = json["charts"]
    traces = []
    layout = json['layout']

    for chartConfig in chartsConfigs:
        request.query_params = chartConfig['query_params'] if 'query_params' in chartConfig else dict()
        request.chart_params = chartConfig['chart_params'] if 'chart_params' in chartConfig else dict()
        chartConfig['params']['request'] = request
        charts = _getChartMethod(chartConfig['method'])(**chartConfig['params'])
        if type(charts) == list:
            for chart in charts :
                for trace in chart.GetChartTrace():
                    traces.append(trace)
        else:
            traces.extend(charts.GetChartTrace())

    return BLM.MultiPlot(traces, layout)

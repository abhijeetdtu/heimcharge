from flask import Blueprint,request,render_template_string

import BusinessLogic.ExceptionHandling as EX
import PresentationLayer.Visualization._chartHelpers as Helpers
import BusinessLogic.Mapping as BLM


ChartPlot = Blueprint('ChartPlot', __name__,template_folder='templates')


@ChartPlot.route("/api/<string:plotName>/<string:resourceName>/<int:xCol>/<int:yCol>/<string:isHorizontal>" , methods = ['GET' , 'POST'])
def apiplot(plotName,resourceName,xCol , yCol,isHorizontal):
    try:
        chart = Helpers._chartPlot(request , plotName , resourceName , xCol,yCol,isHorizontal == "True")
        return Helpers.SetupParamsAndReturnFilePlot("FilePlot",request ,[chart.GetChartHTML()])
    except Exception as e:
        return EX.HandleException(e)

@ChartPlot.route("/chart/<string:plotName>/<string:filename>/<int:xCol>/<int:yCol>" , methods = ['GET' , 'POST'])
def plot(plotName,filename,xCol , yCol):
    try:
        chart = Helpers._chartPlot(request , plotName , filename , xCol,yCol)
        return  Helpers.SetupParamsAndReturnFilePlot("FilePlot",request ,[chart.GetChartHTML()])
    except Exception as e:
        return EX.HandleException(e)

@ChartPlot.route("/trend/<string:api_file>/<string:filename>/<string:yearCols>/<int:yCol>/<string:yVal>" , methods = ['GET' , 'POST'])
def Trend(api_file,filename,yearCols , yCol,yVal='-'):
    try:
        charts = [chart.GetChartHTML() for chart in  Helpers._chartTrend(request,api_file,filename,yearCols , yCol,yVal)]
        return  Helpers.SetupParamsAndReturnFilePlot("FilePlot",request ,charts)
    except Exception as e:
        return EX.HandleException(e)

@ChartPlot.route("/table/<string:filename>/")
def GetTable(filename):
    chart = Helpers._chartTable(filename)
    return Helpers.SetupParamsAndReturnFilePlot("FilePlot",request ,[chart.GetChartHTML()])


@ChartPlot.route("/scatter/<string:filename>/<string:xCol>/<string:yCol>/<int:textCol>")
def scatter( filename,xCol , yCol , textCol):
    try:
        chart = Helpers._chartScatter(request,filename , xCol,yCol,textCol)
        return Helpers.SetupParamsAndReturnFilePlot("FilePlot",request ,[chart.GetChartHTML()])
    except Exception as e:
        return EX.HandleException(e)

@ChartPlot.route("/scattersize/<string:resourceName>/<int:xCol>/<int:yCol>/<int:sizeCol>/<int:textCol>")
def scatterSize( resourceName,xCol , yCol ,sizeCol,textCol):
    try:
        chart = Helpers._chartScatterSize(request ,resourceName,xCol , yCol ,sizeCol,textCol)
        return  Helpers.SetupParamsAndReturnFilePlot("FilePlot",request ,[chart.GetChartHTML()])
    except Exception as e:
        return EX.HandleException(e)

@ChartPlot.route("/stacked/<string:filename>/<int:yCol>/<string:commaSeparatedColumns>")
def stacked(filename,yCol,commaSeparatedColumns):
    try:
        chart = Helpers._chartStackedBar(request ,filename,yCol,commaSeparatedColumns)
        return Helpers.SetupParamsAndReturnFilePlot("FilePlot",request ,[chart.GetChartHTML()])
    except Exception as e:
        return EX.HandleException(e)


@ChartPlot.route("/pie/<string:filename>/<int:yCol>/<string:commaSeparatedColumns>")
def pie(filename,yCol,commaSeparatedColumns):
    try:
        charts = Helpers._chartPie(request,filename,yCol,commaSeparatedColumns)
        return Helpers.SetupParamsAndReturnFilePlot("FilePlot",request ,charts)
    except Exception as e:
        return EX.HandleException(e)

@ChartPlot.route("/multiplot" ,methods=["GET"])
def MultiPlotGet():
    return Helpers.SetupParamsAndReturnFilePlot("MultiPlot",request ,[])

@ChartPlot.route("/multiplot" ,methods=["POST"])
def MultiPlotPost():
    json = request.get_json()
    chartsConfigs = json["charts"]
    traces = []
    layout = json['layout']

    for chartConfig in chartsConfigs:
        request.manual_params = chartConfig['query_params'] if 'query_params' in chartConfig else dict()
        request.chart_params = chartConfig['chart_params'] if 'chart_params' in chartConfig else dict()
        chartConfig['params']['request'] = request
        charts = getattr(Helpers , chartConfig['method'])(**chartConfig['params'])
        if type(charts) == list:
            for chart in charts :
                for trace in chart.GetChartTrace():
                    traces.append(trace)
        else:
            traces.extend(charts.GetChartTrace())

    chart = BLM.MultiPlot(traces, layout)
    return render_template_string(chart.GetChartHTML())

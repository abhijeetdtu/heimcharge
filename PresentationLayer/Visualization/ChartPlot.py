from flask import Blueprint,request,render_template_string

import BusinessLogic.ExceptionHandling as EX
import PresentationLayer.Visualization._chartHelpers as Helpers


ChartPlot = Blueprint('ChartPlot', __name__,template_folder='templates')


@ChartPlot.route("/api/<string:plotName>/<string:resourceName>/<int:xCol>/<int:yCol>/<string:isHorizontal>" , methods = ['GET' , 'POST'])
def apiplot(plotName,resourceName,xCol , yCol,isHorizontal="False"):
    try:
        chart = Helpers._chartPlot(request , plotName , resourceName , xCol,yCol,isHorizontal == "True")
        return Helpers.SetupParamsAndReturnFilePlot("FilePlot",request ,[chart.GetChartHTML()])
    except Exception as e:
        return EX.HandleException(e)

@ChartPlot.route("/chart/<string:plotName>/<string:filename>/<int:xCol>/<int:yCol>/" , methods = ['GET' , 'POST'])
@ChartPlot.route("/chart/<string:plotName>/<string:filename>/<int:xCol>/<int:yCol>/<string:isHorizontal>" , methods = ['GET' , 'POST'])
def plot(plotName,filename,xCol , yCol,isHorizontal="False"):
    try:
        chart = Helpers._chartPlot(request , plotName , filename , xCol,yCol,isHorizontal == "True")
        return  Helpers.SetupParamsAndReturnFilePlot("FilePlot",request ,[chart.GetChartHTML()])
    except Exception as e:
        return EX.HandleException(e)

@ChartPlot.route("/trendanimation/<string:filename>/<string:yearCols>/<string:yCol>/<string:yVal>" , methods = ['GET' , 'POST'])
def trendAnimation(filename,yearCols , yCol,yVal='-'):
    try:
        charts =  Helpers._chartTrendAnimation(request,filename,yearCols , yCol,yVal)
        return  Helpers.SetupParamsAndReturnFilePlot("FilePlot",request ,[charts.GetChartHTML()])
    except Exception as e:
        return EX.HandleException(e)


@ChartPlot.route("/trend/<string:api_file>/<string:filename>/<string:yearCols>/<int:yCol>/<string:yVal>" , methods = ['GET' , 'POST'])
def Trend(api_file,filename,yearCols , yCol,yVal='-'):
    try:
        charts = [chart.GetChartHTML() for chart in  Helpers._chartTrend(request,api_file,filename,yearCols , yCol,yVal)]
        return  Helpers.SetupParamsAndReturnFilePlot("FilePlot",request ,charts)
    except Exception as e:
        return EX.HandleException(e)

@ChartPlot.route("/timeline/<string:filename>/<string:timeCol>/<string:eventCol>")
def timeline(filename,timeCol,eventCol):
    try:
        chart = Helpers._chartTimeline(request,filename,timeCol,eventCol)
        return Helpers.SetupParamsAndReturnFilePlot("FilePlot",request ,[chart.GetChartHTML()])
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
        return Helpers.SetupParamsAndReturnFilePlot("FilePlot",request ,[chart.GetChartHTML() for chart in charts])
    except Exception as e:
        return EX.HandleException(e)


@ChartPlot.route("/multiplot" ,methods=["GET"])
def MultiPlotGet():
    return Helpers.SetupParamsAndReturnFilePlot("MultiPlot",request ,[])

@ChartPlot.route("/multiplot" ,methods=["POST"])
def MultiPlotPost():
    chart = Helpers._chartMultiPlot(request)
    return render_template_string(chart.GetChartHTML())

@ChartPlot.route("/gantt/<string:filename>/<int:yCol>/<string:startCol>/<string:endCol>")
def Gantt(filename,yCol,startCol,endCol):
    try:
        chart = Helpers._chartGant(request,filename,yCol,startCol,endCol)
        return Helpers.SetupParamsAndReturnFilePlot("FilePlot",request ,[chart.GetChartHTML()])
    except Exception as e:
        return EX.HandleException(e)

@ChartPlot.route("/sunburst/<string:filename>/<int:labelCol>/<string:parentCol>/<string:valCol>")
def Sunburst(filename,labelCol , parentCol ,valCol):
    try:
        chart = Helpers._chartSunburst(request,filename,labelCol , parentCol ,valCol)
        return Helpers.SetupParamsAndReturnFilePlot("FilePlot",request ,[chart.GetChartHTML()])
    except Exception as e:
        return EX.HandleException(e)

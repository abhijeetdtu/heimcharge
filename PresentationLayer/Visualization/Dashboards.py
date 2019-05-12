from flask import Blueprint,render_template  , url_for , request ,abort
from jinja2 import TemplateNotFound

import PresentationLayer.Visualization._chartHelpers as Helpers

Dashboards = Blueprint('Dashboards', __name__)


@Dashboards.route('/')
def importantDashboards():
    try:
        dashboards= [ url_for('Dashboards.elections') ,url_for('Dashboards.tourists') , url_for('Dashboards.mutualFunds')  , url_for('Dashboards.civilAviation')   , url_for('Dashboards.stateliteracy') ]
        return render_template('Dashboards/Landing.html' ,dashboard_links = dashboards)

    except TemplateNotFound:
        abort(404)

@Dashboards.route('/tourists')
def tourists():
    try:
        dashboards= [
        {"title":"Tourist Volume" , "url":url_for("ChartPlot.scatter",filename="TourismIndiaOverYears",xCol="1" , yCol ="4", textCol="0",returnPartial="True")}
        ]
        return Helpers.SetupParamsAndReturnTemplate('Dashboards/Base' ,request , dict(dashboard_links = dashboards , carousal=False))

    except TemplateNotFound:
        abort(404)


@Dashboards.route('/mutualFunds')
def mutualFunds():
    try:

        dashboards= [
        {"title":"Mutual Fund Performance" , "url":url_for("ChartPlot.scatter",filename="MutualFundPerformance",xCol=i , yCol =i+1, textCol="0",returnPartial="True")}
        for i in range(3,10)
        ]
        return Helpers.SetupParamsAndReturnTemplate('Dashboards/Base' ,request , dict(dashboard_links = dashboards , carousal=False))

        #dashboards = ['/plot/scatter/MutualFundPerformance/{}/{}/0?returnPartial=True'.format(i,i+1) for i in range(3,10)]

    except TemplateNotFound:
        abort(404)


@Dashboards.route("/civilaviation")
def civilAviation():

    try:

        dashboards= [
        {"title":"Civil Aviation Growth" , "url":url_for("ChartPlot.apiplot" ,plotName= "bar" , resourceName = "aviationcitywisepassengers" , xCol = "4" , yCol = "1" ,isHorizontal = True , returnPartial="True") }
        ]
        return Helpers.SetupParamsAndReturnTemplate('Dashboards/Base' ,request , dict(dashboard_links = dashboards , carousal=False))

    except TemplateNotFound:
        abort(404)

@Dashboards.route("/stateliteracy")
def stateliteracy():

    try:
        dashboards= [
            {"title":"State Literacy" , "url":url_for("ChartPlot.scatterSize" ,resourceName = "stateliteracy" , xCol = "4" , yCol = "7" ,sizeCol="7" , textCol="0" , returnPartial="True") }
        ,   {"collapsable":True,"title": "State Literacy Trend", "url":url_for("ChartPlot.Trend" , api_file='file',filename = "stateliteracy" , yearCols = "4-8" , yCol = "0" ,yVal='-',returnPartial="True")},
        ]
        return Helpers.SetupParamsAndReturnTemplate('Dashboards/Base' ,request , dict(dashboard_links = dashboards , carousal=False))

    except TemplateNotFound:
        abort(404)

@Dashboards.route("/animations")
def Animations():
    try:
        #http://localhost:5000/plot/trendanimation/countrywisetourismoveryears/1-14/0/India
        dashboards= [
            {     "title":"Country Wise Tourism"
                , "url":url_for("ChartPlot.trendAnimation"
                                , filename = "CountryWiseTourismOverYears"
                                , yearCols = "1-14" , yCol = "0" ,yVal="-" , returnPartial=True)
            },
            {     "title":"Seat Shares"
                , "url":url_for("ChartPlot.trendAnimation"
                                , filename = "previouselectionpartyshares"
                                , yearCols = "0-18" , yCol = "T" ,yVal="-" , returnPartial=True , locked={"transpose":"true" ,"animation":{"duration":"1000"}})
            }
        ]
        return Helpers.SetupParamsAndReturnTemplate('Dashboards/Base' ,request , dict(dashboard_links = dashboards , carousal=False))

    except TemplateNotFound:
        abort(404)


@Dashboards.route("/previouselections")
def ElectionsOverYears():

    #http://localhost:5000/plot/scattersize/vidhansabhaelections/0/6/6/1 Vidhan sabha votes polled
    #http://localhost:5000/plot/pie/previouselectionpartyshares/0/2,3,4,5,6,7 Pie Seatshare over past years
    #previouselectionpartyshares/0-18/T/India?locked={"transpose":true,"animation":{"duration":1000}}
    try:
        dashboards = [

            {     "title":"Seat Shares"
                , "url":url_for("ChartPlot.trendAnimation"
                                , filename = "previouselectionpartyshares"
                                , yearCols = "0-18" , yCol = "T" ,yVal="-" , returnPartial=True , locked={"transpose":"true" ,"animation":{"duration":"1000"}})
            },
             {"title":"BJP seats in elections" , "url":url_for("ChartPlot.plot" ,plotName='scatter' , filename = "politicalpartystatus" , xCol = "0" , yCol = "2" ,returnPartial="True")}
            ,{"title":"CPI seats" , "url":url_for("ChartPlot.plot" ,plotName='scatter' , filename = "politicalpartystatus" , xCol = "0" , yCol = "4" ,returnPartial="True")}
            ,{"title":"INC seats" , "url":url_for("ChartPlot.plot" ,plotName='scatter' , filename = "politicalpartystatus" , xCol = "0" , yCol = "6" ,returnPartial="True")}
            ,{"title":"Recognized State Parties seats" , "url":url_for("ChartPlot.plot" ,plotName='scatter' , filename = "politicalpartystatus" , xCol = "0" , yCol = "9" ,returnPartial="True")}
            ,{"title":"Independents seats" , "url":url_for("ChartPlot.plot" ,plotName='scatter' , filename = "politicalpartystatus" , xCol = "0" , yCol = "11" ,returnPartial="True")}
            ,{"title":"Total Other than Recognized Parties seats" , "url":url_for("ChartPlot.plot" ,plotName='scatter' , filename = "politicalpartystatus" , xCol = "0" , yCol = "12" ,returnPartial="True")}
            ,{"title":"Total Expense" , "url":url_for("ChartPlot.plot" ,plotName='bar' , filename = "electionexpenditure" , xCol = "0" , yCol = "5" ,returnPartial="True")}
            ,{"title":"Number of constituencies" , "url":url_for("ChartPlot.plot" ,plotName='bar' , filename = "ElectionsOverYears" , xCol = "0" , yCol = "1" ,returnPartial="True")}
            ,{"title":"Seatshare over past years" , "url":url_for("ChartPlot.pie" , filename = "previouselectionpartyshares" , commaSeparatedColumns = "2,3,4,5,6,7,9,10,11,12" , yCol = "0" ,returnPartial="True")}
         ]
        return Helpers.SetupParamsAndReturnTemplate('Dashboards/Carousal' ,request , dict(dashboard_links = dashboards , carousal=True))

    except TemplateNotFound:
        abort(404)

@Dashboards.route("/elections")
def elections():
    #http://localhost:5000/plot/pie/DateWiseExitPolls2019/1/2,3,4
    try:
        dashboards = [
            {"title":"Past Elections At a Glance","url":url_for("Dashboards.ElectionsOverYears",returnPartial="True")},
            #{"collapsable":True,"title":"Infrastruture Projects" , "url":url_for("ChartPlot.plot" ,plotName='bar' , filename = "InfraProjects" , xCol = "8" , yCol = "7" ,returnPartial="True" , locked={"filter":"8!=Not Available" , "sortby":["Date Of Award","date"]} )},
            {"collapsable":True,"title": "Indian Exports", "url":url_for("ChartPlot.Trend" , api_file='file',filename = "CountryWiseExports" , yearCols = "5-63" , yCol = "0" ,yVal='India',returnPartial="True")},
            {"collapsable":True,"title": "Housing Price Index", "url":url_for("ChartPlot.Trend" , api_file='api',filename = "HousingPriceIndex" , yearCols = "1,2,3,4,5,6,7,8,9,10" , yCol = "0" ,yVal='All India',returnPartial="True")},
            {"collapsable":True,"title": "National Income", "url":url_for("ChartPlot.Trend" , api_file='file',filename = "NationalIncome" , yearCols = "1,2,3,4,5,6,7,8,9,10" , yCol = "0" ,yVal='Per Capita Net National Income (`)',returnPartial="True")},
            {"collapsable":True,"title": "Tourism Revenue", "url":url_for("ChartPlot.Trend" , api_file='api',filename = "TourismRevenue" , yearCols = "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19" , yCol = "0" ,yVal='Monthly- USD mn',returnPartial="True")},
            {"collapsable":True,"title": "FDI TELECOMMUNICATIONS", "url":url_for("ChartPlot.Trend" , api_file='api',filename = "FDI" , yearCols = "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17" , yCol = "0" ,yVal='TELECOMMUNICATIONS',returnPartial="True")},
            {"collapsable":True,"title": "FDI TRADING", "url":url_for("ChartPlot.Trend" , api_file='api', filename = "FDI" , yearCols = "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17" , yCol = "0" ,yVal='TRADING',returnPartial="True")},
            {"collapsable":True,"title": "FDI HOTEL/TOURISM", "url":url_for("ChartPlot.Trend" , api_file='api', filename = "FDI" , yearCols = "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17" , yCol = "0" ,yVal='HOTEL & TOURISM',returnPartial="True")},
            {"collapsable":True,"title": "FDI Retail Trading", "url":url_for("ChartPlot.Trend" , api_file='api', filename = "FDI" , yearCols = "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17" , yCol = "0" ,yVal='RETAIL TRADING',returnPartial="True")},
            {"collapsable":True,"title": "FDI Education", "url":url_for("ChartPlot.Trend" , api_file='api', filename = "FDI" , yearCols = "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17" , yCol = "0" ,yVal='EDUCATION',returnPartial="True")},
            {"collapsable":True,"title": "Terrorist Attacks - Incidents", "url":url_for("ChartPlot.plot" ,plotName='bar' , filename = "TerroristAttacks" , xCol = "0" , yCol = "1" ,returnPartial="True")},
            {"collapsable":True,"title": "Terrorist Attacks - Deaths", "url":url_for("ChartPlot.plot" ,plotName='bar' , filename = "TerroristAttacks" , xCol = "0" , yCol = "2" ,returnPartial="True")},
            {"collapsable":True,"title": "Terrorist Attacks - Injuries", "url":url_for("ChartPlot.plot" ,plotName='bar' , filename = "TerroristAttacks" , xCol = "0" , yCol = "3" ,returnPartial="True")},
            {"collapsable":True,"title": "Consumer Price Index", "url":url_for("ChartPlot.plot" ,plotName='bar' , filename = "ConsumerPriceIndex" , xCol = "1" , yCol = "20" ,returnPartial="True")},
            {"collapsable":True,"title":"Exit Polls 2019" , "url":url_for("ChartPlot.pie" , filename = "DateWiseExitPolls2019" , commaSeparatedColumns = "2,3,4" , yCol = "1" ,returnPartial="True")}
         ]
        return Helpers.SetupParamsAndReturnTemplate('Dashboards/Base' ,request,dict(dashboard_links = dashboards))

    except TemplateNotFound:
        abort(404)

from flask import Blueprint,render_template , Markup , url_for
from jinja2 import TemplateNotFound

from BusinessLogic.Mapping import *
from BusinessLogic.FileOps import *

import os
from config import files

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

        dashboards= [ "/plot/scatter/TourismIndiaOverYears/1/4/0?returnPartial=True" ]

        return render_template('Dashboards/Base.html' ,dashboard_links = dashboards)

    except TemplateNotFound:
        abort(404)


@Dashboards.route('/mutualFunds')
def mutualFunds():
    try:

        dashboards = ['/plot/scatter/MutualFundPerformance/{}/{}/0?returnPartial=True'.format(i,i+1) for i in range(3,10)]


        return render_template('Dashboards/Base.html' ,dashboard_links = dashboards)

    except TemplateNotFound:
        abort(404)


@Dashboards.route("/civilaviation")
def civilAviation():

    try:

        dashboards = [url_for("ChartPlot.apiplot" ,plotName= "bar" , resourceName = "aviationcitywisepassengers" , xCol = "4" , yCol = "1" ,isHorizontal = "h" , returnPartial="True") ]

        return render_template('Dashboards/Base.html' ,dashboard_links = dashboards)

    except TemplateNotFound:
        abort(404)

@Dashboards.route("/stateliteracy")
def stateliteracy():

    try:

        dashboards = [url_for("ChartPlot.scatterSize" ,resourceName = "stateliteracy" , xCol = "4" , yCol = "7" ,sizeCol="7" , textCol=0 , returnPartial="True") ]
        return render_template('Dashboards/Base.html' ,dashboard_links = dashboards)

    except TemplateNotFound:
        abort(404)


@Dashboards.route("/elections")
def elections():
    try:
        dashboards = [
            url_for("ChartPlot.Trend" , api_file='api',filename = "HousingPriceIndex" , yearCols = "1,2,3,4,5,6,7,8,9,10" , yCol = "0" ,yVal='All India',returnPartial="True"),
            url_for("ChartPlot.Trend" , api_file='file',filename = "NationalIncome" , yearCols = "1,2,3,4,5,6,7,8,9,10" , yCol = "0" ,yVal='Per Capita Net National Income (`)',returnPartial="True"),
            url_for("ChartPlot.Trend" , api_file='api',filename = "TourismRevenue" , yearCols = "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19" , yCol = "0" ,yVal='Monthly- USD mn',returnPartial="True"),
            url_for("ChartPlot.Trend" , api_file='api',filename = "FDI" , yearCols = "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17" , yCol = "0" ,yVal='TELECOMMUNICATIONS',returnPartial="True"),
            url_for("ChartPlot.Trend" , api_file='api', filename = "FDI" , yearCols = "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17" , yCol = "0" ,yVal='TRADING',returnPartial="True"),
            url_for("ChartPlot.Trend" , api_file='api', filename = "FDI" , yearCols = "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17" , yCol = "0" ,yVal='HOTEL & TOURISM',returnPartial="True"),
            url_for("ChartPlot.Trend" , api_file='api', filename = "FDI" , yearCols = "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17" , yCol = "0" ,yVal='RETAIL TRADING',returnPartial="True"),
            url_for("ChartPlot.Trend" , api_file='api', filename = "FDI" , yearCols = "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17" , yCol = "0" ,yVal='EDUCATION',returnPartial="True"),
            url_for("ChartPlot.plot" ,plotName='bar' , filename = "TerroristAttacks" , xCol = "0" , yCol = "1" ,returnPartial="True"),
            url_for("ChartPlot.plot" ,plotName='bar' , filename = "TerroristAttacks" , xCol = "0" , yCol = "2" ,returnPartial="True"),
            url_for("ChartPlot.plot" ,plotName='bar' , filename = "TerroristAttacks" , xCol = "0" , yCol = "3" ,returnPartial="True"),
            url_for("ChartPlot.plot" ,plotName='bar' , filename = "ConsumerPriceIndex" , xCol = "1" , yCol = "20" ,returnPartial="True"),
            url_for("ChartPlot.plot" ,plotName='scatter' , filename = "gdp" , xCol = "0" , yCol = "14" ,returnPartial="True"),
            url_for("ChartPlot.Trend" , api_file='api',filename = "FDI" , yearCols = "1,2,3,4,5,6,7" , yCol = "0" ,yVal='EDUCATION',returnPartial="True"),
         ]
        return render_template('Dashboards/Base.html' ,dashboard_links = dashboards)

    except TemplateNotFound:
        abort(404)

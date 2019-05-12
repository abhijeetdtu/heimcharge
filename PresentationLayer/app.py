import sys, traceback , math

from flask import Flask , Markup , render_template,redirect
from flask import request,jsonify

from plotly.offline import plot
from plotly.graph_objs import Scatter
import plotly.graph_objs as go

import BusinessLogic.ExceptionHandling as EX
from BusinessLogic.Mapping import *
from BusinessLogic.FileOps import *
from PresentationLayer.Visualization.IndiaBasePlot import IndiaBasePlot
from PresentationLayer.Visualization.ChartPlot import ChartPlot
from PresentationLayer.Visualization.Dashboards import Dashboards
from PresentationLayer.Visualization.APIPlot import APIPlot

from BusinessLogic.Entities import NavItem
from API.RestBase import Rest

import pdb

application = Flask(__name__ , static_folder="static", template_folder='Templates')

application.register_blueprint(IndiaBasePlot ,url_prefix='/india')
application.register_blueprint(ChartPlot ,url_prefix='/plot')
application.register_blueprint(Dashboards ,url_prefix='/dashboards')
application.register_blueprint(APIPlot, url_prefix="/APIPlot")

application.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
application.config['TEMPLATES_AUTO_RELOAD'] = True
application.jinja_env.auto_reload = True
Rest.SetupCacheDir()

@application.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


@application.errorhandler(404)
def Error404(error):
    return render_template('Errors/404.html'), 404


@application.route("/")
def index():
    try:
        files = GetStateWiseFileList('json')
        navItems = [ NavItem(ConvertFileNameToMeaningful(file) , '/india/plotFileWithMap/{0}/{1}/3?locked={{"autoFitColumnIndex":"true"}}'.format(file.replace(".json", "") , GetLocationColumnFromFile(file.replace(".json", "")))) for file in files]
        return render_template('Landing.html' , nav_items = navItems)

    except Exception as e:
        EX.HandleException(e)
        return Error404(404)


@application.route("/locations")
def locationWise():
    try:
        files = GetStateWiseFileList('json')
        navItems = [ NavItem(ConvertFileNameToMeaningful( file )
                            , '/india/plotFileWithMap/{0}/{1}/3?locked={{"autoFitColumnIndex":"true"}}'.format(file.replace(".json", "")
                            , GetLocationColumnFromFile(file.replace(".json", ""))))
                    for file in files]
        return render_template('Landing.html' , nav_items = navItems)

    except Exception as e:
        EX.HandleException(e)
        return Error404(404)

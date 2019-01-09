import sys, traceback , math

from flask import Flask , Markup , render_template,redirect
from flask import request

from plotly.offline import plot
from plotly.graph_objs import Scatter
import plotly.graph_objs as go

from BusinessLogic.Mapping import *
from BusinessLogic.FileOps import *
from PresentationLayer.Visualization.IndiaBasePlot import IndiaBasePlot
from PresentationLayer.Visualization.ChartPlot import ChartPlot
from PresentationLayer.Visualization.Dashboards import Dashboards
from BusinessLogic.Entities import NavItem


from config import files


application = Flask(__name__ , static_folder="static", template_folder='Templates')

application.register_blueprint(IndiaBasePlot ,url_prefix='/india')
application.register_blueprint(ChartPlot ,url_prefix='/plot')
application.register_blueprint(Dashboards ,url_prefix='/dashboards')

application.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
application.config['TEMPLATES_AUTO_RELOAD'] = True
application.jinja_env.auto_reload = True

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
def Error404():
    return render_template('Errors/404.html'), 404

@application.route("/")
def index():
    try:
        files = GetStateWiseFileList('json')
        navItems = [ NavItem(ConvertFileNameToMeaningful(file) , '/india/plotFileWithMap/{0}/{1}/3?autoFitColumnIndex=true'.format(file.replace(".json", "") , GetStateColumnFromFile(file.replace(".json", "")))) for file in files]
        return render_template('Landing.html' , nav_items = navItems)

    except Exception as e:
        print(e)
        return Error404()


@application.route("/locations")
def locationWise():
    try:
        files = GetStateWiseFileList('json')
        navItems = [ NavItem(ConvertFileNameToMeaningful( file )
                            , '/india/plotFileWithMap/{0}/{1}/3?autoFitColumnIndex=true'.format(file.replace(".json", "")
                            , GetStateColumnFromFile(file.replace(".json", ""))))
                    for file in files]
        return render_template('Landing.html' , nav_items = navItems)

    except Exception as e:
        print(e)
        return Error404()

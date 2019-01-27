import sys, traceback , math
import os

from flask import Flask , Markup , render_template,redirect , url_for
from flask import request,jsonify

from plotly.offline import plot
from plotly.graph_objs import Scatter
import plotly.graph_objs as go


from config import files


application = Flask(__name__ , static_folder="static", template_folder='Templates')


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

        return render_template('Landing.html' , nav_items = [] , d3data = [] )

    except Exception as e:
        print(e)
        return Error404()


@application.route("/imagedata/<int:id>")
def image(id):
    current_path = os.path.dirname(os.path.realpath(__file__))
    print( os.path.dirname(os.path.realpath(__file__)))
    return jsonify(Images(os.path.join(current_path , "static" , "Images", "{0}.jpg".format(id))).EdgeDetection())

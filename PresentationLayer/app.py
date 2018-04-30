from flask import Flask , Markup , render_template
from plotly.offline import plot
from plotly.graph_objs import Scatter

from BusinessLogic.Mapping import *

from PresentationLayer.Visualization.IndiaBasePlot import IndiaBasePlot

application = Flask(__name__ , static_folder="static", template_folder='Templates')

application.register_blueprint(IndiaBasePlot ,url_prefix='/india')


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

@application.route("/")
def hello():

    my_plot_div = plot([Scatter(x=[1, 2, 3 , 5], y=[3, 1, 6 , 15])], output_type='div' ,  config={'displayModeBar': False})
    return render_template('BaseMap.html' , map_content = Markup(m._repr_html_()) , bar_chart = my_plot_div)

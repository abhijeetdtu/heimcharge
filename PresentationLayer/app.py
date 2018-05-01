from flask import Flask , Markup , render_template,redirect
from plotly.offline import plot
from plotly.graph_objs import Scatter

from BusinessLogic.Mapping import *
from BusinessLogic.FileOps import *
from PresentationLayer.Visualization.IndiaBasePlot import IndiaBasePlot

application = Flask(__name__ , static_folder="static", template_folder='Templates')

application.register_blueprint(IndiaBasePlot ,url_prefix='/india')

application.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
application.config['TEMPLATES_AUTO_RELOAD'] = True

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
    return redirect('/india/plotFileWithMap/StateWiseTreeCover/0/2' , code=302)
    xAxisIndex = 2
    yAxisForMap= 2
    df,columns = GetDataFrame('stateWisePopulation')
    colorBy = columns[yAxisForMap]
    df[colorBy] = df[colorBy].astype("float")
    m = IndiaMap(df ,colorBy, [columns[xAxisIndex] , columns[yAxisForMap]])
    return render_template('BaseMap.html' , map=m )

from flask import Blueprint,render_template , Markup
from jinja2 import TemplateNotFound

from BusinessLogic.Mapping import *

import os

IndiaBasePlot = Blueprint('IndiaBasePlot', __name__,template_folder='templates')

@IndiaBasePlot.route('/')
def show():
    try:
        
        dataFile = os.path.abspath(os.path.join("Data" , "stateWisePopulation.json"))
        df = GetDataFrameFromJson(dataFile , PopulationTransform)

        columns = ['India / State/ Union Territory', 'Population 2011']
        colorBy = 'Population 2011'
        m = IndiaMap(df ,colorBy, columns)
        barChart = Markup(BarChart(df , columns[1] , columns[0]  , 'h'))

        return render_template('BaseMap.html' , map_content = Markup(m._repr_html_()) , bar_chart = barChart)

    except TemplateNotFound:
        abort(404)

